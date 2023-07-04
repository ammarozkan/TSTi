import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from tsti.auth import login_required,allowed_file,getExtension
from tsti.db import get_db

from tsti.messages import render_messages

bp = Blueprint('user', __name__,url_prefix='/user')

eastereggfound = 0

@bp.route('/')
def all_users():
    db = get_db()
    ordered_users = db.execute("SELECT id, username, pp_file_name, point, kingdom_id FROM user ORDER BY point DESC").fetchall()
    kingdoms = db.execute("SELECT id, color_hex, kingdomname FROM kingdom ORDER BY id").fetchall()
    ordered_users = [dict(ordered_users[x]) for x in range(0,len(ordered_users))]
    return render_template("all_users.html",users=ordered_users,kingdoms=kingdoms)

@bp.route('/<int:id>')
def userInfo(id):
    db = get_db()
    user_info = db.execute(
        "SELECT id, username, point, kingdom_id, pp_file_name, profile_explanation FROM user WHERE id = ?", (id, )
    ).fetchone()

    messages_html = ''
    message_info = kingdom_info = None
    kingdoms = db.execute("SELECT id, color_hex, kingdomname FROM kingdom ORDER BY id").fetchall()
    if user_info: 
        message_info = db.execute(
                'SELECT p.id, body, created, author_id, username, pp_file_name, kingdom_id, point, answer_to, likes, attachedQuestionID, attachedQuestionSeed, visibility'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' WHERE u.id = ?'
                ' ORDER BY created DESC', (id,)
            ).fetchall()
        if user_info['kingdom_id'] >= 1: kingdom_info = db.execute("SELECT id, color_hex, kingdomname FROM kingdom WHERE id = ?",(user_info['kingdom_id'],)).fetchone()
        for m in message_info:
            if g.user : user_likes = db.execute('SELECT author_id, post_id FROM post_likes WHERE author_id = ?', (g.user["id"],)).fetchall()
            user_likes = [dict(user_likes[x]) for x in range(0,len(user_likes))]
    
            messages_html += render_messages(kingdoms,user_likes,padd=0,id = m['id'],ans = False,explanations = True)

    error = None

    if user_info == None:
        error = "Kullanıcı bulunamadı."

    if error != None:
        flash(error)
    else : return render_template('auth/user_info.html',user_info = user_info, kingdom_info = kingdom_info,messages_html=messages_html)
    return redirect(url_for("index"))

@bp.route('/customisation', methods = ["GET","POST"])
@login_required
def customisation():
    if request.method == "GET":
        elements = [
            ['file','pp_img','Profil Fotoğrafı:','',0],
            ['text','profile_explanation','Açıklama:',g.user['profile_explanation'],1]
            ]
        return render_template('basic_form.html', base_from="base.html",elements=elements,header="Değişiklik İyidir.", formExtras = "enctype=multipart/form-data")
    else :
        file = request.files['pp_img']
        error = None
        db = get_db()
        
        if file and allowed_file(file.filename,{'png','jpg','gif'}):
            file_name = 'userlogos/'+str(g.user["id"])+"."+getExtension(file.filename)
            file.save(os.path.join(current_app.root_path, 'static/'+file_name))
            db.execute('UPDATE user SET pp_file_name = ? WHERE id = ?',(file_name,g.user['id']))
        
        if request.form['profile_explanation'] == None:
            if eastereggfound == 0 : 
                error = "Açıklamasını silmek isteyen adam hiç görmemiştim. İlk oldu."
            else : error = "Açıklamasını silmek isteyen " + str(eastereggfound) + " adam daha görmüştüm. Çok garip adamlarsınız. Ya da aynı adamsın?"
            eastereggfound += 1
        
        if error != None:
            flash(error)
        else:
            db.execute('UPDATE user SET profile_explanation = ? WHERE id = ?',(request.form['profile_explanation'],g.user['id']))
            db.commit()
        
        return redirect(url_for("user.userInfo",id = g.user["id"]))

@bp.route('/warns')
@login_required
def warnings():
    db = get_db()
    
    seen_warnings = db.execute("SELECT created ,warning_type, id_to, warning,warning_from,manager_id FROM warnings WHERE warning_type = 0 AND id_to = ? AND seen = 1 ORDER BY created DESC",(g.user["id"],)).fetchall()
    unseen_warnings = db.execute("SELECT created ,warning_type, id_to, warning,warning_from,manager_id FROM warnings WHERE warning_type = 0 AND id_to = ? AND seen = 0 ORDER BY created DESC",(g.user["id"],)).fetchall()
    db.execute('UPDATE warnings SET seen = 1 WHERE warning_type = 0 AND id_to = ? AND seen = 0 ',(g.user["id"],))
    db.commit()

    kingdom_info = db.execute("SELECT id, color_hex, kingdomname,pp_file_name FROM kingdom ORDER BY id DESC",).fetchall()

    
    return render_template('user/warnings.html',unseen_warnings=unseen_warnings,seen_warnings=seen_warnings,kingdom_info=kingdom_info)
