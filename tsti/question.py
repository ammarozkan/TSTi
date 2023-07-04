from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort

from tsti.auth import login_required
from tsti.db import get_db

bp = Blueprint('question', __name__)

import random, time, os

from tsti.QuestionLib import *

def getQuestion(questionId,seed):
    quest = specificQuestionReader("tsti/tstiQuestions.json",current_app,questionId,seed) #random.randrange(0,len(q["qs"]))
    return quest

@bp.route('/question')
def question():
    seed =  random.randint(0,10000000)
    random.seed(seed)
    #id = random.randrange(0,len(q["qs"]))
    id = random.randrange(0,16)
    quest = specificQuestionReader("tsti/tstiQuestions.json",current_app,id,seed) #random.randrange(0,len(q["qs"]))
    random.seed(int(time.time()))
    return render_template("games/questions.html", p = questionPrinterForHTMLFImage(quest) ,seed = seed,questionId = id)

@bp.route('/question/<int:questionId>/<int:seed>', methods=["GET","POST"])
def question_by_seed(questionId,seed):
    quest = specificQuestionReader("tsti/tstiQuestions.json",current_app,questionId,seed) #random.randrange(0,len(q["qs"]))
    random.seed(int(time.time()))
    p = questionPrinterForHTMLFImage(quest)

    if request.method == "POST":
        db = get_db()
        if db.execute("SELECT author_id, question_seed,question_id FROM question_answers WHERE author_id = ? AND question_seed = ? AND question_id = ?",(g.user["id"],seed,questionId)).fetchone() != None:
            flash("Zaten cevap vermişsin be usta...")
        else:
            isCorrect = True
            # inference control
            if p["type"] == "inference":
                for answer in p["answers"]:
                    if str(answer) not in request.form: isCorrect = False
                for fAnswer in request.form:
                    if int(fAnswer) not in p["answers"]: isCorrect = False
            # equation control
            elif p["type"] == "equation" or p["type"] == "geometric" :
                isCorrect = str(p["answer"]) == request.form["equationanswer"]
            # wwbam control
            elif p["type"] == "wwtbam":
                print(request.form)
                if request.form["questionanswer"] != p["answer"]: isCorrect = False
            
            if isCorrect:
                flash("Braaaavoooooo!!!!")
                solvers = db.execute("SELECT author_id,question_seed from question_answers WHERE question_seed = ? AND question_id = ?",(seed,questionId,)).fetchall()
                x,k = len(solvers),500 # solver count and k = slowityConstant
                questionValue = p["point"]/((100*x/k)+1) # basic mathematical equation that generated from 1/x function for lim x -> infinitiy, f(x) -> 0 and lim x -> 0 f(x) -> p["point"]
                db.execute("UPDATE user SET point = point + ? WHERE id = ?",(int(questionValue),g.user["id"]))
                db.execute("INSERT INTO question_answers (author_id,question_seed,question_id) VALUES (?,?,?)",(g.user["id"],seed,questionId))
                db.commit()
    return render_template("games/questions.html", p = p ,questionId=questionId,seed = seed)

@bp.route('/geometric_like/<int:questionId>/<int:seed>/<geometric_data>/<likeornot>', methods=["GET","POST"])
def geometric_data_like(questionId,seed,geometric_data,likeornot):
    geometric_data = geometric_data[1:len(geometric_data)-1].replace(" ","").split(",")
    geometric_datal = []
    for andata  in geometric_data:
        sptlt = andata.split(".")
        if (not sptlt[0].isnumeric()) and (not sptlt[1].isnumeric()):
            flash("Bilader; yaptığın bu şey ayıptır, günahtır. Laf işitirsin bak.")
            return redirect(url_for("index"))
        geometric_datal.append(float(andata))
    geometric_data = geometric_datal
    
    f = os.path.join(current_app.root_path, 'static/geometric_data/'+"comesfromuser.json")

    with open(f, 'r') as json_file:
        cfuyu = json.load(json_file)
        cfuyu["allgooddatas"].append([*geometric_data,likeornot])
    with open(f,'w') as json_file:
        json.dump(cfuyu,json_file)
    return redirect(url_for("question.question"))
