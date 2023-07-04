import functools

from flask import (Blueprint,flash,g,redirect,render_template,request,session,url_for,current_app)

from werkzeug.security import check_password_hash,generate_password_hash

from tsti.db import get_db

from flask_redmail import RedMail

# for questioning mail verifications
from tsti.QuestionLib import *

bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        error = None

        if not username:
            error = 'Kullanıcı adı lazım.'
        elif not password:
            error = 'Şifre lazım.'
        
        if error is None:
            try:
                db.execute("INSERT INTO user (username,password,email) VALUES (?, ?,?)",(username,generate_password_hash(password),email),)
                db.commit()
            except db.IntegrityError:
                error = f"{username} isimli kullanıcı zaten var. Bu isimde bir kullanıcı daha açılamaz."
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute('SELECT * FROM user WHERE username = ?',(username,)).fetchone()

        if user is None:
            error = 'Geçersiz isim beyim.'
        elif not check_password_hash(user['password'],password):
            error = 'O şifre ne ya? Uymadı o.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash(error)
    return render_template('auth/login.html')

@bp.route('/verify',methods=('GET','POST'))
def email_verify():
    db = get_db()
    if request.method == 'POST':
        answer = request.form['answer']
        error = None
        
        if  g.user["sendedmail_code"] == answer : 
            db.execute("UPDATE user SET email_verified = ? WHERE id = ?",(1,g.user["id"],)) # AttributeError
            flash("Başarıyla doğrulandı.")
            db.commit()
            return redirect(url_for("index"))
        else: flash("Hayır, bu e-postana gelen sorunun doğru cevabı değildi.")
        
        if error != None : flash(error)

    seed =  random.randint(0,10000000)
    random.seed(seed)
    #id = random.randrange(0,len(q["qs"]))
    id = random.choice([0,1,2,3,4])

    quest = specificQuestionReader("tsti/tstiQuestions.json",current_app,id,seed)
    random.seed(int(time.time()))
    questionbody = questionPrinterForHTMLFImage(quest)
    mailbody = render_template("mail_templates/mailquestion.html",p=questionbody)

    db.execute('UPDATE user SET sendedmail_code = ? WHERE id = ?',(questionbody["answer"],g.user["id"],))

    db.commit()

    email = RedMail()
    email.send(
        subject="E-Mail Doğrulama Sorusu",
        receivers=[g.user["email"]],
        html=mailbody
    )
    return render_template('auth/verify.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?',(user_id,)).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif g.user["email_verified"] == 0:
            return redirect(url_for('auth.email_verify'))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        elif g.user["username"]!='zigotvarlibas':
            flash("Bal müşterisi, nabıyon öyle makamının üstü eylemler falan, hayırdır? Zigot Ustanın da dediği gibi:Bal pastanesine ayakla mı giriyosun?")
            return redirect(url_for('messages.index'))
        return view(**kwargs)
    return wrapped_view

#for file defence
def allowed_file(filename,ALLOWED_EXTENSIONS):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def getExtension(filename):
    return filename.rsplit('.',1)[1].lower()
