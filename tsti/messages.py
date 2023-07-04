from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from tsti.auth import login_required
from tsti.db import get_db
from tsti.RDH import user_messageban_control,user_messagesendban_control

bp = Blueprint('messages', __name__, url_prefix='/messages')


        # if ans is true, the function will get messages by answer_to = id. Else the function will get messages by post.id = id.
        # padd means the padding-left for answers. 
def render_messages(kingdoms,user_likes,channel = 0,padd=0,id = -1, ans = True, flip_order = False, explanations = False):
    result = ''
    db = get_db()
    msgs = db.execute(
        'SELECT p.id, body, created, author_id, username, pp_file_name, kingdom_id, point, answer_to, likes, attachedQuestionID, attachedQuestionSeed, visibility'
        ' FROM post p JOIN user u ON p.author_id = u.id'+(' WHERE answer_to = ?' if ans else ' WHERE p.id = ?')+' AND p.channelId = ? AND p.visibility = 1  ORDER BY created '+('DESC' if not flip_order else 'ASC'),
        (id,channel)
    ).fetchall()
    for msg in msgs:
        head = ('' if msg['answer_to'] == -1 else "<a href='"+url_for('messages.specific_post', id = msg['answer_to'])+"'>...</a>") if explanations else ''
        result += render_template('messages/anmessage.html',padd=padd,msg=msg,kingdoms=kingdoms,user_likes=user_likes,head = head,channel = channel)
        result += render_messages(kingdoms,user_likes,channel=channel, padd = padd+5,id = msg['id'],ans = True, flip_order=True)
    
    return result


@bp.route('/', methods=['GET'])
@login_required
@user_messageban_control
def index():
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = "Ulan denyo, nasıl içeriği olmayan bir mesajı paylaşacaksın?"
        elif user_messagesendban_control():
            error = "Mesaj gönderemezsin, bu konuda yasaklısın."
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (body,author_id)'
                'VALUES (?, ?)',
                (body,g.user['id'],))
            db.commit()
    
    db = get_db()
    user_likes = []
    if g.user : user_likes = db.execute('SELECT author_id, post_id FROM post_likes WHERE author_id = ?', (g.user["id"],)).fetchall()
    user_likes = [dict(user_likes[x]) for x in range(0,len(user_likes))]
    kingdoms = db.execute(
        'SELECT id, kingdomname, kingdom_level, color_hex FROM kingdom ORDER BY id ASC'
    ).fetchall()
    return render_template('messages/main.html',msgtext = render_messages(kingdoms,user_likes),user_likes=user_likes)

@bp.route('/send/' , methods=['POST'])
@login_required
@user_messagesendban_control
def send_message():
    db = get_db()
    error = None

    body = request.form['body']
    answer_to = int(request.args.get('answer_to')) if request.args.get('answer_to') != None and request.args.get('answer_to').isdigit() else -1
    channel = int(request.args.get('channel')) if request.args.get('channel') != None and request.args.get('channel').isdigit() else 0

    question_id = int(request.args.get('question_id')) if request.args.get('question_id') != None and request.args.get('question_id').isdigit() else -1
    question_seed = int(request.args.get('question_seed')) if request.args.get('question_seed') != None and request.args.get('question_seed').isdigit() else -1

    if not body:
        error = "Ulan denyo, nasıl içeriği olmayan bir mesajı paylaşacaksın?"
    elif answer_to != -1 and db.execute('SELECT * FROM post WHERE id = ?',(answer_to,)).fetchone() == None:
        error = "Nereye cevap verirsin beyim?"
    elif channel != 0 and db.execute('SELECT * FROM kingdom WHERE id = ?',(channel,)).fetchone() == None:
        error = "Nereye yazarsın beyim?"
        
    if error is not None:
        flash(error)
    else:
        if question_id < 0 and question_seed < 0: db.execute(
                'INSERT INTO post (body,author_id,answer_to ,channelId)'
                'VALUES (?,?,?,?)',
                (body,g.user['id'],answer_to,channel))
        else:
            db.execute(
                'INSERT INTO post (body,author_id, attachedQuestionID, attachedQuestionSeed)'
                'VALUES (?, ?, ?, ?)',
                (body,g.user['id'],question_id,question_seed))
        db.commit()
            
    return redirect(request.referrer)

@bp.route('/<int:id>', methods=['GET'])
@login_required
def specific_post(id):
    db = get_db()
    post = db.execute('SELECT channelId, id FROM post WHERE id = ?',(id,)).fetchone()
    channel = post['channelId'] if post != None and g.user['kingdom_id'] == post['channelId'] else 0

    if g.user : user_likes = db.execute('SELECT author_id, post_id FROM post_likes WHERE author_id = ?', (g.user["id"],)).fetchall()
    user_likes = [dict(user_likes[x]) for x in range(0,len(user_likes))]
    kingdoms = db.execute( 'SELECT id, kingdomname, kingdom_level, color_hex FROM kingdom ORDER BY id ASC' ).fetchall()

    return render_template('messages/main.html',msgtext = render_messages(kingdoms,user_likes,id = id,ans=False, explanations=True,channel=channel),user_likes=user_likes, do_not_show_send_messages = True)
        
    return redirect(url_for('messages.index'))

@bp.route('/like/<int:id>')
@login_required
def like(id):
    db = get_db()
    thePost = db.execute('SELECT likes,id FROM post WHERE id = ?',(id,)).fetchone()
    liked = db.execute('SELECT * FROM post_likes WHERE post_id = ? AND author_id = ? ', (id,g.user['id'],)).fetchone()

    error = None
    if thePost == None:
        error = "Nereyi beğeniyorsun ulan?"
    
    if error != None:
        flash(error)
    else:
        if liked != None:
            db.execute('DELETE FROM post_likes WHERE post_id = ? AND author_id = ? ', (id,g.user['id'],)).fetchone()
            db.execute('UPDATE post SET likes = likes - 1 WHERE id = ?',(id,))
        else:
            db.execute('INSERT INTO post_likes (post_id,author_id) VALUES (?,?)',(id,g.user['id'],))
            db.execute('UPDATE post SET likes = likes + 1 WHERE id = ?',(id,))
        db.commit()
    return redirect(request.referrer)



from tsti.question import getQuestion
from tsti.QuestionLib import questionPrinterForHTMLFImage
import random,time

@bp.route('/sendquestion/<int:questionId>/<int:seed>', methods = ["GET"])
@login_required
def sendQuestion(questionId,seed):
    quest = getQuestion(questionId,seed)
    return render_template("messages/sendquestion.html",p=questionPrinterForHTMLFImage(quest),question_id=questionId,question_seed = seed)


    

@bp.route('/update')
def update():
    return "bbbb"
