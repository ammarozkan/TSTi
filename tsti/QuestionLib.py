import sympy, json, random, time, os
from io import BytesIO
from base64 import b64encode
from tsti.QuestionImageGenerator import getArrayByArrayRule
from tsti.GeoQuestion import *

#
#

# getting ready segment

# premise

def canConcluded(concludeFrom, premises):
    concluded = True
    for c in concludeFrom:
        cCC = False
        for p in premises:
            if p[0] == c : cCC = True
        if not cCC: concluded = False
    return concluded

# equation

def reselectInCondition(vars,dA):
    nonchange = 0
    for condition in dA["conditions"]:
        if condition[2] == 0 and not vars[condition[0]]["val"] == vars[condition[1]]["val"]: vars[condition[0]]["val"] = vars[condition[1]]["val"]
        elif condition[2] == 1 and not vars[condition[0]]["val"] > vars[condition[1]]["val"]: vars[condition[0]]["val"] = random.randrange(vars[condition[1]]["val"],vars[condition[0]]["range"][1])
        elif condition[2] == 2 and not vars[condition[0]]["val"] >= vars[condition[1]]["val"]: vars[condition[0]]["val"] = random.randrange(vars[condition[1]]["val"]-1,vars[condition[0]]["range"][1])
        else: nonchange += 1
    return vars, nonchange==len(dA["conditions"])

def fillFormula(formula,value):
    for val in value:
        formula = formula.subs(value[val]["sympysymbol"],value[val]["val"])
    return formula

def fillTextFormula(formula,value):
    filled = fillFormula(sympy.parse_expr(formula),value)
    return filled 

def productIt(array,vars):
    return [ array[x] if type(array[x]) == int else int(str(sympy.Integer(fillTextFormula(array[x],vars)))) if type(array[x]) == str else array[x] for x in range(0,len(array)) ]

def split_array(array,element):
    s = [[]]
    for arr in array:
        if arr != element:
            s[len(s)-1].append(arr)
        else: s.append([element])
    return s

def sympy_relation(relation):
    if "<=>" in relation:
        cc = relation.split("<=>")
        big_brother = sympy_relation(cc[0])
        for c in cc: big_brother = sympy.logic.boolalg.Equivalent(big_brother,sympy_relation(c))
        relation = big_brother
    elif "=>" in relation:
        cc = relation.split("=>")
        big_brother = sympy_relation(cc[0])
        for j in range(1,len(cc)): big_brother = sympy.logic.boolalg.Implies(big_brother,sympy_relation(cc[j]))
        relation = big_brother
    elif "&" in relation:
        cc = relation.split("&")
        big_brother = sympy_relation(cc[0])
        for j in range(1,len(cc)): big_brother = big_brother & sympy_relation(cc[j])
        relation = big_brother
    elif "|" in relation:
        cc = relation.split("|")
        big_brother = sympy_relation(cc[0])
        for j in range(1,len(cc)): big_brother = big_brother | sympy_relation(cc[j])
        relation = big_brother
    else : return sympy.parse_expr(relation)
    
    return relation

def general_relation(relation, vars):
    relation = relation.split(";")
    for i in range(0,len(relation)):
        '''
        if "<=>" in relation[i]:
            cc = relation[i].split("<=>")
            big_brother = fillTextFormula(cc[0],vars)
            for c in cc: big_brother = sympy.logic.boolalg.Equivalent(big_brother,fillTextFormula(c,vars))
            relation[i] = big_brother
        '''
        if "=>" in relation[i]:
            cc = relation[i].split("=>")
            big_brother = sympy_relation(cc[0])
            if len(cc) != 2 : print("We gotta problem here. sgmnt001")
            try:
                if big_brother: return sympy.parse_expr(cc[1])
            except: pass
            if fillFormula(big_brother,vars): return sympy.parse_expr(cc[1])
    return sympy.parse_expr(relation[0])

def questionHandler(data,current_app): # data : question data
    if data["type"] == "equation":
        definitions = data["image_definitions"] if "image_definitions" in data else {}
        new_def = {}
        for key in definitions: 
            new_def[int(key)] = definitions[key]
        definitions = new_def
        new_def = None

        for var in data["vars"]:
            data["vars"][var]["sympysymbol"] = sympy.symbols(var)
            data["vars"][var]["val"] = random.randrange(data["vars"][var]["range"][0],data["vars"][var]["range"][1])
        nonchange = False
        while not nonchange:
            data["vars"] , nonchange = reselectInCondition(data["vars"],data)

        class explanation_conditions:
            def __init__(self,data_condt):
                self.condt = {}
                for key in data_condt:
                    if "," in key:
                        splitted_key = key.split(",")
                    for k in (splitted_key if len(splitted_key) > 1 else [splitted_key]):
                        self.condt[int(k)] = fillFormula(sympy_relation(data_condt[key]),data["vars"])

            def __getitem__(self,key):
                if key not in self.condt : return True
                else : return fillFormula(self.condt[key],data["vars"])
        
        data_condt = {}
        if "explanation_conditions" in data: data_condt = data["explanation_conditions"]
        sent_condt = explanation_conditions(data_condt)

        for i in range(0,len(data["explanation"])):
            if not sent_condt[i]: 
                data["explanation"][i][0] = "passed"

            elif data["explanation"][i][0] == "symbolic": 
                data["explanation"][i][1] = general_relation(data["explanation"][i][1],data["vars"])
            elif data["explanation"][i][0] == "image":
                array_image_rule = productIt(data["explanation"][i][1],data["vars"])
                for j in range(2,len(array_image_rule)): array_image_rule[j][1] = productIt(array_image_rule[j][1],data["vars"])
                data["explanation"][i][1] = getArrayByArrayRule(array_image_rule,definitions=definitions,one_size_of_element=50,padding=25,space=(25,25))
        
        data_condt = {}
        if "question_conditions" in data: data_condt = data["question_conditions"]
        sent_condt = explanation_conditions(data_condt)

        for i in range(0,len(data["question"])):
            if not sent_condt[i]: 
                data["question"][i][0] = "passed"
            elif data["question"][i][0] == "symbolic": 
                data["question"][i][1] = general_relation(data["question"][i][1],data["vars"])
            elif data["question"][i][0] == "image":
                array_image_rule = productIt(data["question"][i][1],data["vars"])
                for j in range(2,len(array_image_rule)): array_image_rule[j][1] = productIt(array_image_rule[j][1],data["vars"])
                data["explanation"][i][1] = getArrayByArrayRule(array_image_rule,definitions=definitions,one_size_of_element=50,padding=25,space=(25,25))
        
        data["answer"]["val"] = general_relation(data["answer"]["val"],data["vars"])

    elif data["type"] == "inference":
        conclusions = []
        for premise in data["premises"]:
            if random.randrange(0,50) > 25:
                conclusions.append(premise)
        qpremises = []+conclusions

        lastConc = []
        while lastConc != conclusions:
            lastConc=conclusions
            for premise in data["premises"]:
                if premise[3] != 2: continue
                cC = False
                for cFromWhat in premise[1]:
                    if canConcluded(cFromWhat,conclusions): cC = True
                if cC and premise not in conclusions : conclusions.append(premise)

        data["conclusions"] = conclusions
        data["qpremises"] = qpremises
    elif data["type"] == "geometric":
        GL = GeometricLanguager("Basic_Application",False,False,False)
        GL.read_file(linesarray = data["geoquestion_code"])

        f = os.path.join(current_app.root_path, 'static/geometric_data/'+"comesfromuser.json")

        '''
        with open(f, 'r') as json_file:
            gooddatas = json.load(json_file)["allgooddatas"]
        '''
        datafromdots = extractfromdots(GL.plane.dots)

        counter = 1
        #while False in formula_NE6(*datafromdots,gooddatas): # if not beutiful enough, generate again! Beuty calculating with NE6 formula.
        while False in [NE1_fixed(polygon.dots) for polygon in GL.plane.polygons] or NE1_fixed(GL.plane.dots) == False:
            GL = GeometricLanguager("Basic_Application",False,False,False)
            GL.read_file(linesarray = data["geoquestion_code"])
            #datafromdots = extractfromdots(GL.plane.dots)
            counter+=1
        print("I like the "+str(counter)+"nd one.")
        vt = VariableTextor(roundToDigits = 1)

        data["geometric_data"] = datafromdots

        imager = GeometricImager(font_name="tsti/static/fonts/comic.ttf",fontSize = 35,anglei_distance = 30,w=1280,h=600,lineWidth = 2,roundToDigits = 1,rangec=(15,15))
        imager.line_color, imager.dot_color, imager.text_color, imager.background_color = (0,0,0),(255,0,0),(0,0,0),(255,255,255)
        #img = imager.DrawWithVariables(GL.plane,GL.variables)
        img = imager.Draw(GL.plane,debugmode=False)
        data["geometric_image"] = img
        data["allvariables"] = []
        for var in GL.variables:
            if var != "^visible_count" and GL.variables[var]["visibility"]: data["allvariables"].append(vt.textit(GL.variables[var]))
        data["answer"]["val"] = GL[data["answer"]["val"]].value
    elif data["type"] == "wwtbam":
        choices = ["","",""]
        if "genquestionfrom" in data:
            data["questions"] = json.loads(open(data["genquestionfrom"],"r").read())["q"]
        data["question"],data["answer"] = data["questions"].pop(random.randint(0,len(data["questions"])-1))
        for i in range(0,3): _,choices[i] = data["questions"].pop(random.randint(0,len(data["questions"])-1))

        data["choices"] = choices+[data["answer"]]
        random.shuffle(data["choices"])

    return data

#
#

# reading segment

def questionReader(path,current_app):
    with open(path,encoding='utf-8') as f:
        data = json.load(f)

    for i in range(0,len(data["qs"])):
        data["qs"][i] = questionHandler(data["qs"][i],current_app)

    return data

def specificQuestionReader(path,current_app,id = 0,seed = 0):
    with open(path,encoding='utf-8') as f:
        data = json.load(f)
    random.seed(seed)
    result = questionHandler(data["qs"][id],current_app)
    random.seed(int(time.time()))
    return result

#
#

# calculation segment

def questionPrinterForHTMLFImage(data):
    if data["type"] == "equation":
        explanation = ""
        question = ""
        head = data["head"]
        answer = data["answer"]
        #answer["val"] = fillFormula(answer["val"],data["vars"])

        if answer["type"] == "lowestint":
            answer = int(sympy.Integer(fillFormula(answer["val"],data["vars"])+1))
        elif answer["type"] == "float":
            answer = float(sympy.Float(fillFormula(answer["val"],data["vars"])))
        elif answer["type"] == "integer":
            answer = int(sympy.Integer(fillFormula(answer["val"],data["vars"])))
        elif answer["type"] == "bool":
            answer = "Doğru" if answer["val"] == True else "Yanlış"
        elif answer["type"] == "nonint":
            answer = str(fillFormula(answer["val"],data["vars"]))
        else : answer = str(answer["val"])

        for i in range(0,len(data["explanation"])):
            if data["explanation"][i][0] == "passed" : pass
            elif data["explanation"][i][0] == "symbolic":
                explanation += " \\("+str(sympy.latex(fillFormula(data["explanation"][i][1],data["vars"])))+"\\) "
            elif data["explanation"][i][0] == "image":
                image_io = BytesIO()
                data["explanation"][i][1].save(image_io,'PNG')
                textdata = 'data:image/png;base64,'+ b64encode(image_io.getvalue()).decode('ascii')
                explanation += "<image src='"+textdata+"'></image>"
            else : explanation += str(data["explanation"][i][1])
        
        for i in range(0,len(data["question"])):
            if data["question"][i][0] == "passed" : pass
            elif data["question"][i][0] == "symbolic":
                question += " \\("+str(fillFormula(data["question"][i][1],data["vars"]))+"\\) "
            else : question += (str(data["question"][i][1]))
        
        return {"type":"equation","head":head,"explanation":explanation,"question":question,"answer":answer,"point":data["point"]}
    elif data["type"] == "inference":
        tickable = []
        explanation = "<ul>"
        answers = []
        head = data["head"]

        for premise in data["qpremises"]:
            explanation+="<li>"+ premise[2] +"</li>"
        explanation+="</ul>"

        for premise in data["premises"]:
            tickable.append(premise)
        
        for conclusion in data["conclusions"]:
            answers.append(conclusion[0])
        return {"type":"inference","head":head,"explanation":explanation,"tickable":tickable,"answers":answers,"point":data["point"]}
    elif data["type"] == "geometric":
        data["geometric_image"]
        data["answer"]["val"]

        image_io = BytesIO()
        data["geometric_image"].save(image_io,'PNG')
        textdata = 'data:image/png;base64,'+ b64encode(image_io.getvalue()).decode('ascii')
        explanation = "<image width='640' height='300' src='"+textdata+"'></image>"
        for i in range(0,len(data["allvariables"])):
            explanation+="<p>"+data["allvariables"][i]+"</p>"
        question = data["question"]
        head = data["head"]
        answer = str(round(data["answer"]["val"],1))

        return {"type":"geometric","head":head,"explanation":explanation,"question":question,"answer":answer,"point":data["point"],"geometric_data":data["geometric_data"]}

    elif data["type"] == "wwtbam":

        '''image_io = BytesIO()
        data["geometric_image"].save(image_io,'PNG')
        textdata = 'data:image/png;base64,'+ b64encode(image_io.getvalue()).decode('ascii')
        explanation = "<image width='640' height='300' src='"+textdata+"'></image>"
        for i in range(0,len(data["allvariables"])):
            explanation+="<p>"+data["allvariables"][i]+"</p>"
        question = data["question"]
        head = data["head"]
        answer = str(round(data["answer"]["val"],1))'''

        return data


