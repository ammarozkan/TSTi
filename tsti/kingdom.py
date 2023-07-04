import os,functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,current_app
)
from werkzeug.exceptions import abort

from tsti.auth import login_required,allowed_file,getExtension
from tsti.db import get_db
from tsti.messages import render_messages

bp = Blueprint('kingdom', __name__,url_prefix='/kingdom')

# 4 : Yonetici
# 0 : Normal Halk (bildiğin köylü)
ranknames = ["Köylü","Moderin","Kraliyet Büyüğü","Yardımcı","Lord"]

reqPerm = 3

@bp.route('/')
def kingdom_main():
    db=get_db()
    kingdoms = db.execute("SELECT id, kingdomname, kingdom_exp, kingdom_level, color_hex, pp_file_name FROM kingdom ORDER BY kingdom_level").fetchall()
    usersDict = dict()
    for kingdom in kingdoms:
        print(kingdom['pp_file_name'])
        usersDict[kingdom["id"]] = db.execute("SELECT id, username, point, level, kingdom_id, kingdom_perm FROM user WHERE kingdom_id = ? ORDER BY kingdom_perm DESC, point DESC",(kingdom["id"],)).fetchall()

    user_requests = []
    req_sended_kingdoms = []
    if g.user: 
        user_requests= db.execute("SELECT r.id, r.user_id, r.join_desc, r.kingdom_id, k.kingdomname FROM kingdom_requests r INNER JOIN kingdom k ON r.kingdom_id = k.id WHERE user_id = ?",(g.user["id"],)).fetchall()
        req_sended_kingdoms = db.execute("SELECT kingdom_id FROM kingdom_requests WHERE user_id = ?",(g.user["id"],)).fetchall()
        req_sended_kingdoms = [dict(req_sended_kingdoms[x]) for x in range(0,len(req_sended_kingdoms))]
    
    return render_template(
        "kingdom/main.html", 
        kingdoms = kingdoms,
        users = usersDict,
        user_requests = user_requests,
        req_sended_kingdoms = req_sended_kingdoms,
        ranknames = ranknames)


@bp.route('/join/<int:kingdom_id>', methods = ("GET","POST"))
@login_required
def join_kingdom(kingdom_id):
    if request.method == "POST":
        db = get_db()
        join_desc = request.form["join_desc"]
        error = None

        if g.user["kingdom_id"] != 0:
            error = "Zaten bir kraliyete üyesin."
        elif join_desc == None:
            error = "İstek yollamak için bir açıklama lazım."
        elif len(db.execute("SELECT id FROM kingdom WHERE id = ?" , (kingdom_id,)).fetchall()) == 0:
            error = "Öyle bir kraliyet yok?"
        
        if error != None:
            flash(error)
        else:
            if len(db.execute("SELECT id,kingdom_id FROM user WHERE kingdom_id = ?",(kingdom_id,)).fetchall()) == 0:
                flash("Kraliyette kimse olmadığından, artık sen yöneticisin.")
                db.execute("UPDATE user SET kingdom_id = ?, kingdom_perm = 4 WHERE id = ?",(kingdom_id,g.user["id"],))
                db.execute("DELETE FROM kingdom_requests WHERE user_id = ?",(g.user["id"],))
            else:
                db.execute("INSERT INTO kingdom_requests (user_id,join_desc,kingdom_id) VALUES (?,?,?)",(g.user["id"],join_desc,kingdom_id,))
            db.commit()
        return redirect(url_for("kingdom.kingdom_main"))
    return render_template("kingdom/join_request.html")

@bp.route('/join/cancel/<int:requestId>', methods = ["POST"])
@login_required
def cancel_request_kingdom(requestId):
    db = get_db()
    db.execute("DELETE FROM kingdom_requests WHERE id = ?",(requestId,))
    db.commit()
    return redirect(url_for("kingdom.kingdom_main"))

def kingdom_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user["kingdom_id"] == 0:
            flash("Ya bir linke tıkladın yada yazdın, ne yaptın bilemem ama bunu yapamazsın.")
            return redirect(url_for('kingdom.kingdom_main'))
        return view(**kwargs)
    return wrapped_view

def kingdom_perm_required(perm):
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user["kingdom_perm"] < perm:
                flash("Bunun için kraliyet yönetim izini gerekir paşam.")
                return redirect(url_for('kingdom.kingdom_main'))
            return view(**kwargs)
        return wrapped_view
    return decorator

@bp.route('/exit', methods= ("GET","POST"))
@login_required
@kingdom_required
def exit_kingdom():
    if request.method == "GET":
        return render_template("kingdom/exit_kingdom.html")
    elif request.method == "POST":
        if g.user["kingdom_id"] != 0:
            db = get_db()
            flash("Dostum umarım birisi site açığı kullanarak seni çıkarmamıştır ama sanırım az önce klanından çıkış yaptın.")
            kingdom_id = g.user["kingdom_id"]
            db.execute("UPDATE user SET kingdom_id = ?, kingdom_perm = 0 WHERE id = ?",(0,g.user["id"],))
            print(g.user["username"]," exited from ",kingdom_id,".")

            admin = db.execute("SELECT id, kingdom_id, kingdom_perm, point FROM user WHERE kingdom_id = ? AND kingdom_perm = 4",(kingdom_id,)).fetchall()
            if len(admin) == 0:
                best_user = db.execute("SELECT id, kingdom_id, kingdom_perm, point FROM user WHERE kingdom_id = ? ORDER BY kingdom_perm DESC, point DESC",(kingdom_id,)).fetchone()
                if best_user != None: db.execute("UPDATE user SET kingdom_perm = ? WHERE id = ?",(4,best_user["id"]))
            db.commit()
            return redirect(url_for("kingdom.kingdom_main"))
    return redirect(url_for("index"))

@bp.route('/mine', methods = ["GET"])
@login_required
@kingdom_required
def user_kingdom():
    db = get_db()

    users_inkingdom = db.execute("SELECT id, username, point, level, kingdom_id, kingdom_perm FROM user WHERE kingdom_id = ? ORDER BY kingdom_perm DESC, point DESC",(g.user["kingdom_id"],)).fetchall()
    kingdom = db.execute("SELECT id, kingdomname, kingdom_exp, kingdom_level, color_hex,pp_file_name FROM kingdom WHERE id = ?",(g.user["kingdom_id"],)).fetchone()
    kingdom_requests = db.execute("SELECT r.id, r.user_id, r.join_desc, r.kingdom_id, u.username, u.point FROM kingdom_requests r INNER JOIN user u ON u.id = r.user_id WHERE r.kingdom_id = ?", (g.user["kingdom_id"],)).fetchall()
    unseen_warning = db.execute("SELECT created ,warning_type, id_to, warning FROM warnings WHERE warning_type = 1 AND id_to = ? AND seen = 0 ORDER BY created DESC",(g.user['kingdom_id'],)).fetchall()
    seen_warning = db.execute("SELECT created ,warning_type, id_to, warning FROM warnings WHERE warning_type = 1 AND id_to = ? AND seen = 1 ORDER BY created DESC",(g.user['kingdom_id'],)).fetchall()

    kingdoms = db.execute(
        'SELECT id, kingdomname, kingdom_level, color_hex FROM kingdom ORDER BY id ASC'
    ).fetchall()
    user_likes = db.execute('SELECT author_id, post_id FROM post_likes WHERE author_id = ?', (g.user["id"],)).fetchall()
    user_likes = [dict(user_likes[x]) for x in range(0,len(user_likes))]
    kingdom_messages_html = render_messages(kingdoms,user_likes,channel=g.user['kingdom_id'])

    db.execute('UPDATE warnings SET seen = 1 WHERE warning_type = 1 AND id_to = ? AND seen = 0 ',(g.user['kingdom_id'],))
    db.commit()
    return render_template("kingdom/user_kingdom.html",users_inkingdom = users_inkingdom, kingdom = kingdom,kingdom_requests=kingdom_requests, ranknames = ranknames,seen_warnings=seen_warning,unseen_warnings=unseen_warning, kingdom_messages_html = kingdom_messages_html)

@bp.route('/apply/<int:request_id>', methods = ("GET","POST"))
@login_required
@kingdom_required
@kingdom_perm_required(3)
def apply_kingdom(request_id):
    if request.method == "GET":
        flash("Hayırdır?")
        print("USTA BİRİSİ LİNK İLEN apply_kingdom'a girdi haaaaaa, haberin olsun diye yani. Giren de ", g.user["username"], " benden duymuş olma.")
        return redirect(url_for("kingdom.user_kingdom"))
    db = get_db()
    that_request = db.execute("SELECT id, user_id, kingdom_id FROM kingdom_requests WHERE id = ?",(request_id,)).fetchone()
    error = None

    if that_request == None:
        error = "Böyle bir istek göremedim. Ya bende sıkıntı var, ya da beni yazan meymenetsizde!"

    if error != None:
        flash(error)
    else:
        db.execute("UPDATE user SET kingdom_id = ?, kingdom_perm = 0 WHERE id = ?",(that_request["kingdom_id"],that_request["user_id"]))
        db.execute("DELETE FROM kingdom_requests WHERE user_id = ?",(that_request["user_id"],))
        db.commit()
    
    return redirect(url_for("kingdom.user_kingdom"))

@bp.route('/ban/<int:user_id>', methods=['POST'])
@login_required
@kingdom_required
@kingdom_perm_required(3)
def ban_user_kingdom(user_id):
    db = get_db()
    banned_in_future_user = db.execute("SELECT username, kingdom_id, kingdom_perm, id FROM user WHERE id = ?",(user_id,)).fetchone()
    error = None
    if banned_in_future_user == None:
        error = "Bak canım benim, nasıl yaptın bilmiyorum ama şuan yaptığın şey çok ilginç. Ya sen tam tıklarken kullanıcı bir anda silindi yada yoktan kendine buton yarattın. Vallahi ilginç."
    elif banned_in_future_user["kingdom_id"] != g.user["kingdom_id"]:
        error = "Haaa?! Nasıl kraliyette olmayan birini banlamak için link bulup da tıklayabilirsin ki? Tabii ki sen yapmadıysan, orası ayrı."
    elif banned_in_future_user["kingdom_perm"] >= g.user["kingdom_perm"]:
        error = "Usta bu adamı banlamak için daha çok ekmek yemen lazım. Kalkışırsan böyle şeylere, didişirsin kahpe şeylerle!"
    
    if error != None:
        flash(error)
        print("Bak buraya müdür! Birisi çok ilginç bişeyler deniyor haberin olsun haa. Hatası da bu : ", error)
        return redirect(url_for('index'))
    else:
        db.execute("UPDATE user SET kingdom_id = 0, kingdom_perm = 0 WHERE id = ? AND kingdom_id = ? AND kingdom_perm < ?",(user_id,g.user["kingdom_id"],g.user["kingdom_perm"],))
        db.commit()
        return redirect(url_for('kingdom.user_kingdom'))

@bp.route('/rank_up/<int:user_id>', methods=['POST'])
@login_required
@kingdom_required
@kingdom_perm_required(3)
def rank_up_kingdom(user_id):
    db = get_db()
    rankedup_in_future_user = db.execute("SELECT username, kingdom_id, kingdom_perm, id FROM user WHERE id = ?",(user_id,)).fetchone()
    error = None
    if rankedup_in_future_user == None:
        error = "Bak canım benim, nasıl yaptın bilmiyorum ama şuan yaptığın şey çok ilginç. Ya sen tam tıklarken kullanıcı bir anda silindi yada yoktan kendine buton yarattın. Vallahi ilginç."
    elif rankedup_in_future_user["kingdom_id"] != g.user["kingdom_id"]:
        error = "Haaa?! Nasıl kraliyette olmayan birini yükseltmek için link bulup da tıklayabilirsin ki? Tabii ki sen yapmadıysan, orası ayrı."
    elif rankedup_in_future_user["kingdom_perm"]+1 >= g.user["kingdom_perm"]:
        error = "Usta bu adamı yükseltmek için daha çok ekmek yemen lazım. Kalkışırsan böyle şeylere, didişirsin kahpe şeylerle!"
    
    if error != None:
        flash(error)
        print("Bak buraya müdür! Birisi çok ilginç bişeyler deniyor haberin olsun haa. Hatası da bu : ", error)
    else:
        db.execute("UPDATE user SET kingdom_perm = kingdom_perm + 1 WHERE id = ? AND kingdom_id = ? ",(user_id, g.user["kingdom_id"]))
        db.commit()
    return redirect(url_for('kingdom.user_kingdom'))


@bp.route('/edit', methods=('GET','POST'))
@login_required
@kingdom_required
@kingdom_perm_required(4)
def edit_kingdom():
    db = get_db()
    if request.method == 'GET':
        preval = db.execute("SELECT color_hex, kingdom_exp,kingdomname FROM kingdom WHERE id = ?", (g.user["kingdom_id"],)).fetchone()

        elements = [
            ['file','pp_img','Profil Fotoğrafı:','',0],
            ['text','kingdomname','Kraliyet İsmi:',preval['kingdomname'],0],
            ['color','color_hex','Renk:',preval['color_hex'],1],
            ['text','kingdom_exp','Açıklama:',preval['kingdom_exp'],1]
            ]

        return render_template('basic_form.html', base_from="base.html",elements=elements,header="Kraliyetini Düzenle!", formExtras = "enctype=multipart/form-data")
    else:
        error = None

        file = request.files['pp_img']
        if file and allowed_file(file.filename,{'png','jpg','gif'}):
            file_name = 'kingdomlogos/'+str(g.user["id"])+"."+getExtension(file.filename)
            file.save(os.path.join(current_app.root_path, 'static/'+file_name))
            db.execute('UPDATE kingdom SET pp_file_name = ? WHERE id = ?',(file_name,g.user['kingdom_id']))
        
        if request.form["kingdom_exp"] == None:
            error = "Açıklama nerede usta?"
        elif request.form["color_hex"] == None:
            error = "Renk? Renk... REnk??!!"
        elif request.form["kingdomname"] == None:
            error = "İsmi olmayan kraliyet mi olur ulaaayn?!"

        if error != None:
            flash(error)
        else : 
            db.execute("UPDATE kingdom SET color_hex = ?, kingdom_exp = ?, kingdomname = ? WHERE id = ?",(str(request.form["color_hex"]),str(request.form["kingdom_exp"]),str(request.form["kingdomname"]),g.user["kingdom_id"]))
            db.commit()
        return redirect(url_for("kingdom.user_kingdom"))

@bp.route('/remove/<int:id>', methods=['POST'])
@login_required
@kingdom_required
@kingdom_perm_required(4)
def remove_message_kingdom(id):
    db = get_db()
    db.execute("UPDATE post SET visibility = 0 WHERE id = ?",(id,))
    db.commit()

    return redirect(request.referrer)

@bp.route('/warning_to/<int:user_id>', methods=['GET','POST'])
@login_required
@kingdom_required
@kingdom_perm_required(4)
def warning_kingdom(user_id):
    if request.method == 'GET':
        elements = [
            ['text','warn','Uyarı:','',1]
            ]
        return render_template('basic_form.html', base_from="base.html",elements=elements,header="Kullanıcıya Uyarı. Kahpe herif!", formExtras = "")
    else:
        error = None
        warn_text = request.form['warn']

        if warn_text == None:
            error = "Uyarı kısımı boş olamaz."
        if error != None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO warnings (id_to,warning_type,manager_id,warning,warning_from) VALUES (?,?,?,?,?)',(user_id,0,g.user['kingdom_id'],warn_text,1))
            db.commit()


    return redirect(url_for('kingdom.user_kingdom'))