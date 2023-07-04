import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash,generate_password_hash

from tsti.auth import login_required
from tsti.db import get_db


bp = Blueprint('RDH', __name__,url_prefix="/management")


def management_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.manager is None:
            return redirect(url_for('RDH.login'))
        return view(**kwargs)
    return wrapped_view

def user_messageban_control(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['ban']%4 == 0:
            flash("Mesaj göremezsin, bu konuda yasaklısın.")
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view

def user_messagesendban_control(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user['ban']%2 == 0:
            flash("Mesaj gönderemezsin, bu konuda yasaklısın.")
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view

def user_login_control(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user != None and g.user['ban']%5 == 0:
            flash("Bu kayıtlı kullanıcı yasaklı.")
            session['user_id'] = None
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view

def LOGIT(subject_id, indpart_id, explanation, manager_id):
    db = get_db()
    db.execute('INSERT INTO happened (subject_id, indpart_id, explanation, manager_id) VALUES (?,?,?,?)',(subject_id, indpart_id, explanation, manager_id,))
    db.commit()


@bp.route("/report/<repType>/<int:id>", methods=["GET","POST"])
@login_required
def report(repType,id):
    db = get_db()
    if request.method == 'GET':
        return render_template("management/report.html",nosee=True,blank = False)
    else:
        infoFR = request.form['infoFR']
        error = None
        if infoFR == None:
            error = "Raporlamak için sebebe ihtiyaç var."
        if error != None:
            flash(error)
        else:
            if repType == "messages":
                db.execute('INSERT INTO reports (report_type,author_id,i_id,infoFR) VALUES (?,?,?,?)',(0,g.user["id"],id,infoFR))
                db.commit()
                flash("Mesaj başarıyla raporlandı.")
                return redirect(url_for("messages.specific_post",id=id))
            elif repType == "kingdom":
                db.execute('INSERT INTO reports (report_type,author_id,i_id,infoFR) VALUES (?,?,?,?)',(1,g.user["id"],id,infoFR))
                db.commit()
                flash("Kraliyet başarıyla raporlandı.")
                return redirect(url_for("kingdom.kingdom_main"))
            elif repType == "user":
                db.execute('INSERT INTO reports (report_type,author_id,i_id,infoFR) VALUES (?,?,?,?)',(2,g.user["id"],id,infoFR))
                db.commit()
                flash("Kullanıcı başarıyla raporlandı.")
                return redirect(url_for("user.userInfo",id=id))
    
    return render_template("management/report.html",nosee=True,blank = True)

@bp.route('/')
@management_required
def index():
    return render_template("management/index.html")

@bp.route("/login", methods = ["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        manager = db.execute('SELECT * FROM managers WHERE username = ?',(username,)).fetchone()

        if manager is None:
            error = 'Geçersiz isim beyim.'
        elif not check_password_hash(manager['password'],password):
            error = 'O şifre ne ya? Uymadı o.'
        
        if error is None:
            session['manager_id'] = manager['id']
            LOGIT(0,0,"Yönetici girişi.",manager['id'])
            return redirect(url_for('RDH.index'))
        
        flash(error)
    
    return render_template('management/login.html')

@bp.route("/logout", methods = ["GET","POST"])
def logout():
    LOGIT(0,0,"Yönetici çıkışı.",g.manager['id'])
    session['manager_id'] = None
    return redirect(url_for('index'))

@bp.route("/plug_in", methods = ["GET","POST"])
def management_plug_in():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        ultimatepassword = request.form['ultimatepassword']
        db = get_db()
        if ultimatepassword == "12345":
            try:
                db.execute("INSERT INTO managers (username,password) VALUES (?, ?)",(username,generate_password_hash(password)),)
                db.commit()
            except db.IntegrityError:
                print(f"{username} kullanıcı adıyla yönetici hesabı açımı denendi.")
            else:
                LOGIT(0,0,"Yönetici oluşturumu. Oluşturulan yönetici:"+username,0)
    return render_template('management/notfound.html')

@bp.route('/ultimatepassword')
def ultimatepassword():
    return render_template('management/register_manager.html')

@bp.before_app_request
@user_login_control
def load_logged_in_manager():
    manager_id = session.get('manager_id')

    if manager_id is None:
        g.manager = None
    else:
        g.manager = get_db().execute('SELECT * FROM managers WHERE id = ?',(manager_id,)).fetchone()
        if g.manager : print("YÖNETİCİ '"+g.manager['username']+"':"+request.url)



# users

@bp.route("/users")
@management_required
def users():
    db = get_db()
    users = db.execute('SELECT * FROM user ORDER BY id ASC').fetchall()
    users = [dict(users[x]) for x in range(0,len(users))]
    return render_template("management/users.html", users=users)

@bp.route("/user/<int:id>")
@management_required
def an_user(id):
    db = get_db()
    user = dict(db.execute('SELECT * FROM user WHERE id = ?',(id,)).fetchone())
    return render_template("management/an_user.html", user=user)

@bp.route('/banuser/<int:id>/<int:by>')
@management_required
def banuser(id,by):
    db = get_db()
    db.execute('UPDATE user SET ban = ban*? WHERE id = ?',(by,id,))
    LOGIT(id,by,"Kullanıcı "+str(by)+" ile banlandı.",g.manager['id'])
    db.commit()
    return redirect(url_for('RDH.an_user',id=id))

@bp.route('/unbanuser/<int:id>/<int:by>')
@management_required
def unbanuser(id,by):
    db = get_db()
    if by > 0:
        db.execute('UPDATE user SET ban = ban/? WHERE id = ?',(by,id,))
        LOGIT(id,by,"Kullanıcı "+str(by)+" ile banı kaldırıldı.",g.manager['id'])
        db.commit()
    return redirect(url_for('RDH.an_user',id=id))

@bp.route('/banuser/<int:id>/point0/')
@management_required
def banuser_point0(id):
    db = get_db()
    db.execute('UPDATE user SET point = 0 WHERE id = ?',(id,))
    LOGIT(id,0,"Kullanıcının puanı sıfırlandı.",g.manager['id'])
    db.commit()
    return redirect(url_for('RDH.an_user',id=id))

@bp.route('/bannedusers/<int:by>')
@management_required
def bannedusers(by):
    db = get_db()
    banneduser_list = db.execute('SELECT * FROM user WHERE ban%? = 0',(by,)).fetchall()
    banneduser_list = [dict(banneduser_list[x]) for x in range(0,len(banneduser_list))]
    return render_template("basic_list.html", base_from="management/base.html",list_object=banneduser_list,list_name=str(by)+" ile banlanan kullanıcılar.")


@bp.route('/editkingdom/<int:id>', methods=["GET","POST"])
@management_required
def edit_kingdom(id):
    db = get_db()
    if request.method == 'GET':
        preval = db.execute("SELECT color_hex, kingdom_exp,kingdomname FROM kingdom WHERE id = ?", (id,)).fetchone()
        elements = [
            ['text','kingdomname','Kraliyet İsmi:',preval['kingdomname'],1],
            ['textarea','kingdom_exp','Açıklama:',preval['kingdom_exp'],1],
            ['color','color_hex','Renk:',preval['color_hex'],1],
            ['text','warning','Bir Uyarıda Bulunmak İstersen:','',0]
        ]
        return render_template("basic_form.html", base_from="management/base.html", elements = elements,header='Kraliyet Düzenle')
    else:
        error = None
        if request.form["kingdom_exp"] == None:
            error = "Açıklama nerede usta?"
        elif request.form["color_hex"] == None:
            error = "Renk? Renk... REnk??!!"
        elif request.form["kingdomname"] == None:
            error = "İsmi olmayan kraliyet mi olur ulaaayn?!"

        if error != None:
            flash(error)
        else : 
            db.execute("UPDATE kingdom SET color_hex = ?, kingdom_exp = ?, kingdomname = ? WHERE id = ?",(str(request.form["color_hex"]),str(request.form["kingdom_exp"]),str(request.form["kingdomname"]),id))

            if request.form['warning'] != None:
                db.execute('INSERT INTO warnings (id_to,warning_type,manager_id,warning) VALUES (?,?,?,?)',(id,1,g.manager['id'],request.form['warning']))
                LOGIT(id,-1 if request.args.get('report_id') == None else request.args.get('report_id') ,"Kraliyette değişiklik ile birlikte uyarı yapıldı..",g.manager['id'])
            
            if request.args.get('report_id') != None:
                print(request.args.get('report_id')," DEGISTI")
                db.execute('UPDATE reports SET visibility = 0 WHERE report_id = ?',(request.args.get('report_id'),))
                LOGIT(id,request.args.get('report_id'),"() Rapor " + g.manager['username'] + " kraliyette değişikliğe uğratılarak onaylandı.",g.manager['id'])
            db.commit()
        return redirect(request.referrer)


#managers

@bp.route("/managers")
@management_required
def managers():
    db = get_db()
    managers_list = db.execute('SELECT * FROM managers ORDER BY id ASC').fetchall()
    managers_list = [dict(managers_list[x]) for x in range(0,len(managers_list))]
    return render_template("basic_list.html", base_from="management/base.html", list_object=managers_list,list_name="Yöneticiler")

# reports and happennings

@bp.route("/reports")
@management_required
def reports():
    db = get_db()
    messages = db.execute('SELECT id, author_id, created, body, likes, answer_to, attachedQuestionID, attachedQuestionSeed FROM post ORDER BY id ASC').fetchall()
    messages = [dict(messages[x]) for x in range(0,len(messages))]

    kingdoms = db.execute('SELECT * from kingdom ORDER BY id ASC').fetchall()
    kingdoms = [dict(kingdoms[x]) for x in range(0,len(kingdoms))]

    mbyId = dict()
    for m in messages:
        mbyId[m["id"]] = m
    reports = db.execute('SELECT report_id, report_type, author_id, i_id, report_state, infoFR FROM reports WHERE visibility = 1 ORDER BY report_state DESC').fetchall()
    users = db.execute('SELECT id, username, password FROM user ORDER BY id ASC').fetchall()
    return render_template("management/reports.html",reports = reports, messages = mbyId, users=users,kingdoms = kingdoms)

@bp.route('/reports/deny/<int:id>')
@management_required
def deny_report(id):
    db = get_db()
    db.execute('UPDATE reports SET visibility = 0 WHERE report_id = ?',(id,))
    LOGIT(-1,id,"(,report_id) Rapor " + g.manager['username'] + " tarafından reddedildi.",g.manager['id'])
    db.commit()
    return redirect( url_for('RDH.reports') )

@bp.route('/remove_post/<int:report_id>/<int:id>')
@management_required
def remove_post(report_id,id):
    db = get_db()
    report = db.execute('SELECT author_id FROM reports WHERE report_id = ?',(report_id,)).fetchone()
    db.execute('UPDATE reports SET visibility = 0 WHERE report_type = 0 AND i_id = ?',(id,))
    post = db.execute('SELECT author_id FROM post WHERE id = ?',(id,)).fetchone()
    db.execute('UPDATE post SET visibility = 0,likes = 0 WHERE id = ?',(id,))

    LOGIT(post['author_id'],report_id,"() Raporlanan mesaj silindi.",g.manager['id'])
    db.commit()
    return redirect(url_for("RDH.reports"))

@bp.route('/posts')
@management_required
def posts():
    db = get_db()
    msgs = db.execute(
        'SELECT p.id, body, created, author_id, username, kingdom_id, point, answer_to, likes, attachedQuestionID, attachedQuestionSeed, visibility'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    msgs = [dict(msgs[x]) for x in range(0,len(msgs))]
    return render_template("basic_list.html", base_from="management/base.html",list_object=msgs,list_name = "Mesajlar") 

@bp.route('/happeneds')
@management_required
def happeneds():
    db = get_db()
    happs = db.execute('SELECT * FROM happened ORDER BY created DESC').fetchall()
    happs = [dict(happs[x]) for x in range(0,len(happs))]
    return render_template("basic_list.html", base_from="management/base.html",list_object=happs,list_name = "Olanlar")

@bp.route('/old_reports')
@management_required
def old_reports():
    db = get_db()
    happs = db.execute('SELECT * FROM reports').fetchall()
    happs = [dict(happs[x]) for x in range(0,len(happs))]
    return render_template("basic_list.html", base_from="management/base.html",list_object=happs,list_name = "Raporlar")

@bp.route('/warning/<string:type>/<int:id>', methods=["GET","POST"])
@management_required
def send_warning(type,id):
    if request.method == "POST":
        warning_text = request.form['warning']
        db = get_db()
        warning_type = 0 if type == 'user' else 1 if type == 'kingdom' else -1
        error = None
        if warning_type == -1:
            error = "Uyarı tipi anlaşılamadı."
        
        if error != None:
            flash(error)
        else :
            lenwarning = len(db.execute('SELECT id FROM warnings').fetchall())
            LOGIT(id,-1 if request.args.get('report_id') == None else request.args.get('report_id') ,"(user(id),report(report_id))"+type+" uyarısı Yapıldı. (Uyarı ID:"+str(lenwarning+1)+")",g.manager['id'])
            db.execute('INSERT INTO warnings (id_to,warning_type,manager_id,warning) VALUES (?,?,?,?)',(id,warning_type,g.manager['id'],warning_text))
            if request.args.get('report_id') != None:
                db.execute('UPDATE reports SET visibility = 0 WHERE report_id = ?',(request.args.get('report_id'),))
            db.commit()

    elements = [['text','warning','Uyarıyı Giriniz:','',1]]
    return render_template('basic_form.html', base_from="management/base.html",elements=elements,header="Uyari")

#database

@bp.route('/database')
@management_required
def database():
    db = get_db()
    database_name = ''
    condition = ''
    if request.args.get('name') != None: database_name = request.args.get('name')
    if request.args.get('search') != None and request.args.get('equalto') != None and request.args.get('search') != '' and request.args.get('equalto') != '': condition = ' WHERE '+request.args.get('search')+'='+request.args.get('equalto')


    happs = db.execute("SELECT * FROM "+( 'sqlite_master' if database_name == "" else database_name ) +condition).fetchall()
    happs = [dict(happs[x]) for x in range(0,len(happs))]
    
    return render_template("basic_list.html", base_from="management/base.html",list_object=happs,list_name = "Database "+database_name,urlfora = "RDH.database",namefora="name")