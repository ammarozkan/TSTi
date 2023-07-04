import os

from flask import Flask, render_template, g
from flask_redmail import RedMail

zigotsentences = [
    "Milat, zekanın ve kudretin ufuk çizgisi kadar belirli olduğu yerdir.",
    "Damadın bulunmadığı yerde şan şöhret, kalem bulunmadığı yerde malem mühmet aranmaz.",
    "Klan kurmak en büyük şeref unsurlarından ve liderlik vasıflarından bir tanesidir.",
    "Bir grupta üye toplamak, klanın başındaki kişinin hitap ve liderlik yeteneği olduğunu gösterir.",
    "Zigotu olmayanın bey(i)ni de olmaz derler. Ben inanmam. Ben çalışmaya inanırım. Far-",
    "Kestane yenir, bazen yenmez, bazen çok yenir, bazen çürüktür.",
    "Yiyin için, taa ki biri sizi yediğinizden men edinceye kadar. Men eden ya kendiniz ya da mideniz.",
    "Şifremi bilene Kamil, bilmeyene damir derim.",
    "Bal pastanesine ayakla mı giriyorsun?"
]



def create_app(test_config=None):
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'tsti.sqlite'),
    )
    
    app.config["EMAIL_HOST"] = "smtp.gmail.com"
    app.config["EMAIL_PORT"] = 587

    import json
    with open("tsti/secretinformation.json",'r') as json_file:
        si = json.load(json_file)
        app.config["EMAIL_USERNAME"] = si["EMAIL_USERNAME"]
        app.config["EMAIL_PASSWORD"] = si["EMAIL_PASSWORD"]
        app.config["EMAIL_SENDER"] = si["EMAIL_SENDER"]
    email = RedMail(app)


    if test_config is None:
        app.config.from_pyfile('config.py',silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import messages
    app.register_blueprint(messages.bp)

    from . import puzzle
    app.register_blueprint(puzzle.bp)

    from . import question
    app.register_blueprint(question.bp)

    from . import user
    app.register_blueprint(user.bp)

    from . import kingdom
    app.register_blueprint(kingdom.bp)

    from . import RDH
    app.register_blueprint(RDH.bp)
    
    from . import questioneditor
    app.register_blueprint(questioneditor.bp)

    @app.context_processor
    def context_processor():
        dbb = db.get_db()
        zvSentences = dbb.execute('SELECT body,created,username FROM post INNER JOIN user ON user.id = post.author_id WHERE username = "zigotvarlibas" AND visibility = 1 AND channelId = 0').fetchall()
        zvLiked = dbb.execute(
            'SELECT l.author_id,p.visibility,  p.created, p.body, lu.username FROM post_likes  AS l '
            ' INNER JOIN post AS p ON l.post_id = p.id '
            ' INNER JOIN user AS u ON l.author_id = u.id '
            ' INNER JOIN user AS lu ON p.author_id = lu.id'
            ' WHERE u.username = ? AND p.visibility = 1 AND p.channelId = 0', ("zigotvarlibas",)
            ).fetchall()
        unseen_warn_count = 0
        if g.user != None: 
            unseen_warn_count = len(dbb.execute("SELECT created ,warning_type, id_to, warning,warning_from FROM warnings WHERE warning_type = 0 AND id_to = ? AND seen = 0 ORDER BY created DESC",(g.user["id"],)).fetchall())

        def path_exists(path_in_tsti):
            return os.path.exists(app.root_path+path_in_tsti)
        return dict(zvSentences = zvSentences,basesentences=zigotsentences, zvLiked=zvLiked, path_exists = path_exists,unseen_warn_count = unseen_warn_count)


    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app