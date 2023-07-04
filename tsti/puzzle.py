from . import PuzzleLib
import random

from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from tsti.auth import login_required, admin_required
from tsti.db import get_db

bp = Blueprint('puzzle', __name__)

puzzlesize = 3
letters=['X','Y','Z','A','B','C','D','E','F']
winsentences=[
    " buldu.",
    " çözdü."
]
losesentences=[
    " bilemedi.",
    " tutturamadı.",
    " yapamadı."
]

import json

def savetojson(diction,path):
    with open(path,"w") as outfile:
        outfile.write( json.dumps(diction, indent=4) )

def loadfromjson(path):
    return json.load(open(path))

def savepuzzle(puzzlename, puzzleset ,path="tsti/puzzledata.json"):
    data = loadfromjson(path)
    data[puzzlename] = puzzleset
    savetojson(data,path)

def loadpuzzle(puzzlename, path="tsti/puzzledata.json"):
    return loadfromjson(path)[puzzlename]



@bp.route('/dailypuzzle', methods = ('GET','POST'))
@login_required
def daily_puzzle():
    if request.method == 'POST':
        puzzle = loadpuzzle('dailysquaret2')
        error = None
        if [[g.user["username"],g.user["id"]],True] in puzzle["solver"] or [[g.user["username"],g.user["id"]],False] in puzzle["solver"] : error = "Zaten cevabını yollamışsın balık adam?"
        elif len(request.form.getlist('answer[]')) != len(puzzle["question"]) : "Bir saniye dostum. Siteye girdiğin şeyler hakkında ufak bir problemimiz var."
        for a in request.form.getlist('answer[]') : 
            try:
                int(a)
            except:
                error = "Bir saniye dostum siteye girdiğin şeyler hakkında bir problemimiz var."
        
        if error: flash(error)
        else:
            answer = [int(x) for x in request.form.getlist('answer[]')]
            atr = True
            db = get_db()
            
            for x in range(0,len(answer)):
                if puzzle["puzzle"][puzzle["question"][x][1]][puzzle["question"][x][0]]!=int(answer[x]) : atr = False
            puzzle["solver"].append([[g.user["username"],g.user["id"]],atr])
            savepuzzle('dailysquaret2',puzzle)
            if atr: 
                db.execute("UPDATE user SET point = point + 10 WHERE id = ?",(g.user["id"],))
                db.commit()
    dailypuzzledict = loadpuzzle("dailysquaret2")
    return render_template('games/squaret2.html', dailypuzzledict = dailypuzzledict,letters=letters, w=winsentences,l=losesentences)

@bp.route('/resetpuzzle')
@admin_required
def resetpuzzle():
    #my library for generating 3 or more puzzles from one exact rule
    s = [PuzzleLib.Squaret2(puzzlesize) for x in range(0,3)]
    rule = s[0].randomRule()
    characters = [i for i in range(0,10)]
    for x in range(0,len(s)): s[x].calculateRule(rule,st_value = characters.pop(random.randint(0,len(characters)-1)))

    diction = {"infos":[s[x].base for x in range(0,len(s)-1)],"puzzle":s[len(s)-1].base , "question":[], "solver":[], "unsolver":[]}

    for x in range(0,9):
        if random.randrange(0,5) < 2:
            diction["question"].append([x%puzzlesize,int(x/puzzlesize)])
    if len(diction["question"]) == 0: diction["question"] = [[random.randrange(0,puzzlesize),random.randrange(0,puzzlesize)]]

    savepuzzle("dailysquaret2",diction)
    
    return redirect(url_for("puzzle.daily_puzzle"))