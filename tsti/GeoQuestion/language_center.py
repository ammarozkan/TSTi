from .variables import *
import random
from math import pi

class Variable:
    def __init__(self,name,value,specifies_dict=dict(),visibility=True):
        self.name, self.value, self.specifies_dict, self.visibility = name, value, specifies_dict,visibility

    def __getitem__(self, key):
        if key == "value": return self.value
        elif key == "name": return self.name
        elif key == "visibility": return self.visibility
        elif key in self.specifies_dict: return self.specifies_dict[key]

    def __str__(self):
        return self.name + ":" + str(self.specifies_dict) + "=" + str(self.value) + " that " + ("visible" if self.visibility else "not visible")

class VariableTextor:
    def __init__(self,roundToDigits=3):
        self.area_notation = lambda name, value : "A("+name+") = "+str(value)
        self.distance_notation = lambda name, value : "|"+name+"| = "+str(value)
        self.angle_notation = lambda name, value : "m("+name+") = "+str(value)
        self.roundToDigits=roundToDigits

    def textit(self,anvar):
        value = anvar["value"] if self.roundToDigits == -1 else round(anvar["value"],self.roundToDigits)
        notation = lambda name, value: str(name)+" = "+str(value)
        if anvar["type"] == "distance":notation = self.distance_notation
        elif anvar["type"] == "area": notation = self.area_notation
        elif anvar["type"] == "angle": notation = self.angle_notation

        return notation(anvar["objectname"],value)

class Finder:
    def __init__(self):
        self.founded_id = -1

    def find_by_name(self,array,name):
        for i in range(0,len(array)):
            if array[i].name == name:
                self.founded_id = i
                return True
    
    def find_by_name_plane(self,plane,name,obj_type):
        object_id = plane.find_object_by_name_(name,obj_type)
        if object_id != None:
            self.founded_id = object_id
            return True
        return False


class GeometricLanguager:
    def __init__(self, project_name, error_log_printing = True, info_log_printing = True,megainfo_log_printing = True,output_log_printing=True):
        self.project_name = project_name
        self.plane = Plane()
        self.constant1 = (-10,10)
        self.constant2 = (-10,10)
        self.rereads = dict()

        self.finder = Finder()
        self.variables = {"^visible_count":0}

        self.error_log_printing = error_log_printing
        self.info_log_printing = info_log_printing
        self.megainfo_log_printing = megainfo_log_printing
        self.output_log_printing = True
    
    def to_dict(self,string : str):
        variables = string.split(",")
        result = dict()
        for variable in variables:
            name, value = tuple(variable.split(":"))
            result[name] = value.split(";")
            result[name] = result[name][0] if len(result[name]) == 1 else result[name]
        return result

    def convert_lyritic(self,string : str):
        string = string.lstrip().split(" ")
        belong_to  = False
        priv_value = False
        priv_segment = False
        commands = False
        if "'s" in string[0][-2:]:
            belong_to = string[0][0:-2]
            if len(string) > 1:
                priv_value = string[1]
            if len(string) > 2:
                priv_segment = string[2]
        else:
            commands = string
        return {"belong_to":belong_to,"priv_value":priv_value,"priv_segment":priv_segment,"commands":commands}

    def error_log(self,*l):
        if self.error_log_printing: print("ERROR:",*l)

    def info_log(self,*l):
        if self.info_log_printing: print("Info:",*l)

    def output_log(self, *l):
        if self.output_log_printing: print(*l)

    def megainfo_log(self,*l):
        if self.megainfo_log_printing: print("MegaInfo:",*l)

    
    def read_file(self,file_path = None,linesarray = None):
        if linesarray == None and file_path != None:
            with open(file_path) as fp:
                linesarray = fp.readlines()
                self.info_log("Reading File:",file_path)
        elif linesarray == None:
            self.error_log("Hey, hey, hey. Somethings wrong... You cant just pass a empty parameter here!")
        
        for line in linesarray:
            self.megainfo_log("Reading Steilen:",line)
            if line[0:4] != "next" and line[0:3] != "end":
                line = line.replace("\n","").split("->")
                var_data = self.to_dict(line[1].replace(" ",""))
                if "name" in var_data and var_data["name"] == "^visible_count":
                    self.error_log("You need to define a name to your thing that is not '^visible_count'")
                if line[0].replace(" ","") == "line":
                    if "name" not in var_data:
                        self.error_log("If you defining a line, you should define with a name in it!")
                    elif len(line) == 3:
                        prop = line[2].lstrip().split(" ")
                        if len(prop) == 3 and "'s" in prop[0]:
                            self.info_log("calculating ", prop[0].replace("'s","")+"'s ",prop[1]," for ",prop[2])
                            object_name = prop[0].replace("'s","")
                            object_id = self.plane.find_object_by_name_( object_name,Polygon )
                            object = None
                            successfullycreated = True
                            if object_id != None: object = self.plane.polygons[object_id]
                            if object == None:
                                self.error_log("There is not a polygon named "+object_name," can you check it?")
                                successfullycreated = False
                            elif prop[1] == "median":
                                self.plane.add_object(object.median_line(object.getdotid(prop[2]),var_data["name"]),var_data["name"])
                            elif prop[1] == "prependicular":
                                self.plane.add_object(object.prependicular_line(object.getdotid(prop[2]),var_data["name"]),var_data["name"])
                            elif prop[1] == "bisector":
                                d2dotid = object.getdotid(prop[2])
                                if d2dotid == -1: self.error_log("There is not ",prop[2]," named dot.")
                                else: 
                                    d2id = object.polygonStyleOrdered_ids.index(d2dotid)
                                    d1 = object.polygonStyleOrdered_ids[(d2id-1)%len(object.dots)]
                                    d2 = object.polygonStyleOrdered_ids[d2id]
                                    d3 = object.polygonStyleOrdered_ids[(d2id+1)%len(object.dots)]

                                    self.plane.add_object(object.bisector(d1,d2,d3,var_data["name"]),var_data["name"])
                            else:
                                self.error_log("What is an, ",prop[1],"?")
                                successfullycreated = False
                            if successfullycreated: self.info_log(object_name,"'s ",prop[2]," ",prop[1]," setted to line ",var_data["name"])
                        else:
                            self.error_log("If a line defining by another segment, you should use that syntax: -> [triangle_name]'s [thing] [that_dot's]")
                    elif len(line) == 2:
                        k = None
                        c = None
                        if "parallel" in var_data:
                            k = self.plane.lines[self.plane.find_object_by_name_(var_data["parallel"],Function)].const[1]
                        if "c" in var_data:
                            c = float(var_data["c"])
                        if "k" in var_data:
                            k = float(var_data["k"])
                        self.plane.create_beuty_random_line(var_data["name"],self.constant1,k=k,c=c)
                        self.info_log("Line Defined:",var_data["name"])

                    else: self.error_log("Wtf is that. You splitted ",len(line)," times your line with that '->' thing.")
                elif line[0].replace(" ","") == "dot" or line[0].replace(" ","") == "secretdot":
                    secretdot = line[0].replace(" ","") == "secretdot"
                    if "name" not in var_data:
                        self.error_log("If you are defining a dot, you should define with a name in it!")
                    elif "cut" not in var_data or len(var_data["cut"]) != 2 or type(var_data["cut"]) != list:
                        self.error_log("If you are defining a dot, you should define with 2 cuts in it!")
                    else:
                        f1 = self.plane.find_object_by_name_(var_data["cut"][0],Function)
                        f2 = self.plane.find_object_by_name_(var_data["cut"][1],Function)
                        if      f1 == None: self.error_log("I don't know line '",var_data["cut"][0],"'. You know?")
                        elif    f2 == None: self.error_log("I don't know line '",var_data["cut"][1],"'. You know?")
                        else:
                            self.plane.intersect_and_set(f1,f2,var_data["name"],not secretdot)
                            self.info_log("Dot Defined:",var_data["name"])
                elif line[0].replace(" ","") == "triangle":
                    if "name" not in var_data:
                        self.error_log("If you are defining a triangle, you should define with a name in it!")
                    elif "dots" not in var_data or len(var_data["dots"]) != 3:
                        self.error_log("If you are defining a triangle, you should define with 3 dots in it!")
                    else:
                        self.plane.define_polygon_(var_data["name"],True,*var_data["dots"])
                elif line[0].replace(" ","") == "freetriangle":
                    if "name" not in var_data:
                        self.error_log("If you are defining a triangle, you should define with a name in it!")
                    elif "dots" not in var_data or len(var_data["dots"]) != 3:
                        self.error_log("If you are defining a triangle, you should define with 3 or more dots in it!")
                    else:
                        self.plane.define_freepolygon_(var_data["name"],True,*var_data["dots"])
                        self.info_log("Defined a freepolygon named "+var_data["name"]+"!")
                elif line[0].replace(" ","") == "polygon":
                    if "name" not in var_data:
                        self.error_log("If you are defining a polygon, you should define with a name in it!")
                    elif "dots" not in var_data or len(var_data["dots"]) < 3:
                        self.error_log("If you are defining a polygon, you should define with 3 or more dots in it!")
                    else:
                        self.plane.define_polygon_(var_data["name"],len(var_data["dots"]) == 3,*var_data["dots"])
                elif line[0].replace(" ","") == "freepolygon":
                    if "name" not in var_data:
                        self.error_log("If you are defining a polygon, you should define with a name in it!")
                    elif "dots" not in var_data or len(var_data["dots"]) < 3:
                        self.error_log("If you are defining a polygon, you should define with 3 or more dots in it!")
                    else:
                        self.plane.define_freepolygon_(var_data["name"],len(var_data["dots"]) == 3,*var_data["dots"])
                        self.info_log("Defined a freepolygon named "+var_data["name"]+"!")
                elif line[0].replace(" ","") == "variable":
                    lyritic = self.convert_lyritic(line[2])
                    visibility = False if "visible" not in var_data or var_data["visible"]!="yes" else True
                    if visibility: self.variables["^visible_count"]+=1
                    if lyritic["belong_to"]:
                        if lyritic["priv_value"] and lyritic["priv_value"] == "area":
                            if self.finder.find_by_name_plane(self.plane,lyritic["belong_to"],Polygon):
                                specifies_dict = {"type":"area","objectname":self.plane.polygons[self.finder.founded_id].polygon_name()}
                                self.variables[var_data["name"]] = Variable(var_data["name"],self.plane.polygons[self.finder.founded_id].area(),specifies_dict,visibility)
                        elif lyritic["priv_value"] and lyritic["priv_value"] == "angle":
                                if self.finder.find_by_name_plane(self.plane,lyritic["belong_to"],Polygon):
                                    object = self.plane.polygons[self.finder.founded_id]
                                    d2dotid = object.getdotid(lyritic["priv_segment"])
                                    if d2dotid == -1: self.error_log("There is not ",lyritic["priv_segment"]," named dot.")
                                    anglevalue = self.plane.polygons[self.finder.founded_id].angles[d2dotid]*180/pi
                                    allangles = [object.dots[object.polygonStyleOrdered_ids[(i+object.polygonStyleOrdered_ids.index(d2dotid)-1)%len(object.dots)]].name for i in range(0,3)]
                                    specifies_dict = {"type":"angle","objectname":allangles[0]+allangles[1]+allangles[2]}
                                    self.variables[var_data["name"]] = Variable(var_data["name"],anglevalue,specifies_dict,visibility)
                                    d2dotid = object.getdotid(lyritic["priv_segment"])
                                    if d2dotid == -1: self.error_log("There is not ",lyritic["priv_segment"]," named dot.")
                                    else:
                                        object.angles[d2dotid]
                    elif lyritic["commands"]:
                        if lyritic["commands"][0] == "lengthof":
                            d_ids = [-1,-1]
                            for i in range(0,2):
                                if self.finder.find_by_name_plane(self.plane,lyritic["commands"][i+1],Dot):
                                    d_ids[i] = self.finder.founded_id
                            if -1 not in d_ids:
                                specifies_dict = {"type":"distance","objectname":self.plane.dots[d_ids[0]].name+self.plane.dots[d_ids[1]].name}
                                self.variables[var_data["name"]] = Variable(var_data["name"],Dot.distance_of_points(self.plane.dots[d_ids[0]],self.plane.dots[d_ids[1]]),specifies_dict,visibility)
                        else: self.error_log("We dont know such a command:",lyritic["commands"][0])



            else:
                line = line.replace("\n","").split(" ")
                if line[0] == "next":
                    if line[1] == "to":
                        self.read_file(line[2])
                    elif line[1] == "is":
                        if line[2] == "reread":
                            if line[3] not in self.rereads: 
                                self.rereads[line[3]] = int(line[4])
                        elif line[2] == "graphing":
                            self.show_result()
                        elif line[2] == "clear":
                            self.info_log("Clear--\n\n")
                            self.plane.clear()
                        elif line[2] == "log":
                            self.output_log("LOG:\n",self.plane)
                            self.output_log("Variables:")
                            for var in self.variables:
                                self.output_log(var,":",self.variables[var])
                        else: self.error_log("What is ",line[2],"? What should I do? I don't know wth is that!")
                    else: self.error_log("Hmmm... Let's talk about '",line[1],"' that you write at next segment...")

        if file_path in self.rereads and self.rereads[file_path] != 0:
            self.rereads[file_path] = self.rereads[file_path] - 1
            self.info_log("I seen, I should continue to reading my destiny... And I should do it ",self.rereads[file_path]," times at ",file_path,"...")
            self.read_file(file_path)
                        
    
    def show_result(self):
        self.plane.to_graph()

    def __getitem__(self,name):
        for var in self.variables:
            if var == name: return self.variables[var]
                            
        
        
