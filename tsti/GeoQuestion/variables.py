import math
from .primary_functions import easyatan,order_dots_by_OutAngleRule,select_from_,order_dots_polygonStyle_by_intersecteds_andReceiveOnlyIds,avarage,avrdistance,std_dev,fixval,fixdistance
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from random import random,randint

class Coordinate:
    def __init__(self,coordinates):
        self.x,self.y = coordinates
    def __add__(self,U):
        if type(U) == tuple:
            return Coordinate((self.x+U[0],self.y+U[1]))
        return Coordinate((self.x+U.x,self.y+U.y))
    def __sub__(self,U):
        if type(U) == tuple:
            return Coordinate((self.x-U[0],self.y-U[1]))
        return Coordinate((self.x-U.x,self.y-U.y))
    def __mul__(self, other : float):
        return Coordinate((self.x*other,self.y*other))
    def __rmul__(self, other : float):
        return Coordinate((self.x*other,self.y*other))
    def __truediv__(self,other: float):
        return Coordinate((self.x/other,self.y/other))
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+")"
    def slope(self):
        return self.y/self.x
    def getArrayLike(self):
        return [self.x,self.y]
    def getTupleLike(self):
        return (self.x,self.y)
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    def rotate(self,angle_in_rad : float,center_point=None):
        if center_point == None: center_point = Coordinate((0,0))
        x = center_point.x - self.x
        y = center_point.y - self.y
        A = math.sqrt(x**2 + y**2)
        alpha = easyatan(y/x)
        return Coordinate((A*math.sin(alpha+angle_in_rad),A*math.sin(alpha+angle_in_rad)))
    
    @staticmethod
    def average_of_coordinates(points):
        sumofcoord = Coordinate((0,0))
        c = 0
        for point in points:
            sumofcoord = point+sumofcoord
        return sumofcoord/len(points)

    @staticmethod
    def distance_of_coords(c1,c2):
        return math.sqrt((c2.x-c1.x)**2 + (c2.y-c1.y)**2)

class Dot:
    def __init__(self,coordinate,name,visibility=True):
        if type(coordinate) == Coordinate:
            self.coord = coordinate
        elif type(coordinate) == tuple:
            self.coord = Coordinate(coordinate)
        self.name = name
        self.visibility = visibility
    
    def rotate(self,angle_in_rad : float, center_point = Coordinate((0,0))):
        return Dot((self.coord.rotate(angle_in_rad,center_point)),self.name+"'")
    
    def __add__(self,u): # u should be coord
        coord_ = (u.coord + self.coord)
        return Dot((coord_.x,coord_.y),self.name+"MIXED"+u.name)
    def __mul__(self,k : float):
        coord_ = self.coord*k
        return Dot((coord_.x,coord_.y),self.name+"MIXED")
    def __rmul__(self,k : float):
        coord_ = self.coord*k
        return Dot((coord_.x,coord_.y),self.name+"MIXED")
    def __truediv__(self,k : float):
        coord_ = self.coord/k
        return Dot((coord_.x,coord_.y),self.name+"MIXED")
    
    def __str__(self):
        return ("{"+self.name+":"+str(self.coord.getArrayLike())+"}")
    
    @staticmethod
    def average_of_points(points):
        sumofcoord = Dot((0,0),"")
        c = 0
        for point in points:
            sumofcoord = point+sumofcoord
        return sumofcoord/len(points)

    @staticmethod
    def distance_of_points(p1,p2):
        return Coordinate.distance_of_coords(p1.coord, p2.coord)
    

class Function:
    def __init__(self,constants,name): # constants = [k0, k1, k2, k3...] => f(x) = k0 + k1*x + k2*x**2 + k3*x**3...
        self.const = constants
        self.name = name
    
    def f(self,x):
        r = self.const[0]
        for c in range(1,len(self.const)):
            r += self.const[c]*(x**c)
        return r

    def __call__(self,x):
        return self.f(x)
    
    def f_numpy(self,xr):
        r = self.const[0]*np.ones(len(xr))
        for c in range(1,len(self.const)):
            r = r + self.const[c]*(xr**c)
        return r
    
    def fcoord(self,x):
        return Coordinate((x,self.f(x)))
    
    def dx_by_vectorsize(self,size):
        if len(self.const) == 2: 
            return math.sqrt((size**2)/(self.const[1]**2+1))

    def __str__(self):
        functext = ""
        for c in range(0,len(self.const)):
            i = len(self.const)-c-1
            x_power = i
            str_value = str(float(int(self.const[i]*100))/100)
            functext += ("+" if self.const[i] > 0 and c != 0 else "")+(str_value+"x^"+str(i) if i > 1 else str_value+"x" if i > 0 else str_value)
        return self.name+":"+functext
    
    @staticmethod
    def coordsToLine(coord1 : Coordinate,coord2 : Coordinate,name):
        basic_line = coord2-coord1
        k = basic_line.y/basic_line.x
        c = coord1.y-k*coord1.x
        return Function([c,k],name)

    @staticmethod
    def deriative(function):
        return Function([function.const[i]*i for i in range(1,len(function.const))],function.name+"'")

    @staticmethod
    def dotsToLine(dot1 : Dot,dot2 : Dot, name):
        return Function.coordsToLine(dot1.coord,dot2.coord,name)
    
    @staticmethod
    def dotAndSlope(dot : Dot,slope, name):
        c = dot.coord.y-slope*dot.coord.x
        return Function([c,slope],name)
    
    @staticmethod
    def intersect(f1,f2):
        x = (f2.const[0]-f1.const[0])/(f1.const[1]-f2.const[1])
        y = (f2.const[1]*f1.const[0]-f1.const[1]*f2.const[0])/(f2.const[1]-f1.const[1])
        return Coordinate((x,y))
    
    @staticmethod
    def rotate_line(line,angle_in_rad : float, center_point = Coordinate((0,0))):
        a1,a2 = line.fcoord(0).rotate(angle_in_rad,center_point),line.fcoord(1).rotate(angle_in_rad,center_point)
        return Function.dotsToLine(a1,a2)
    
    @staticmethod
    def random_line_byAngle(name = "randomline"+str(randint(0,99999999999)),slope_range = (0,math.pi),c_range = (-10,10)):
        angle = (slope_range[1]-slope_range[0]) * random() + slope_range[0]
        constant = (c_range[1]-c_range[0]) * random() + c_range[0]
        return Function([constant,easyatan(angle)],name)
    
    @staticmethod
    def random_line_withC_byAngle(name = "randomline"+str(randint(0,99999999999)),slope_range = (0,math.pi),c = 0):
        angle = (slope_range[1]-slope_range[0]) * random() + slope_range[0]
        return Function([c,easyatan(angle)],name)
    
    @staticmethod
    def random_line_parallelto_(another_line,name = "randomline"+str(randint(0,99999999999)),c_range = (-10,10)):
        constant = (c_range[1]-c_range[0]) * random() + c_range[0]
        return Function([constant,another_line.const[1]],name)
    
    @staticmethod
    def random_line_withC_parallelto_(another_line,name = "randomline"+str(randint(0,99999999999)),c = 0):
        return Function([c,another_line.const[1]],name)
        



class Polygon:
    
    def __init__(self, dots : list[Dot],lines_of_intersecteds,name): 
            # if constants_of_intersecteds = [(Function([1,0]), Function([0,1]))] => dots[0] occurs from intersection of f(x) = 1 with f(x) = x
        self.dots,lines_of_intersecteds = order_dots_by_OutAngleRule(dots,lines_of_intersecteds)
        angles = [0 for c in range(0,len(self.dots))]
        for x in range(0,len(self.dots)):
            angles[x] = abs( easyatan(lines_of_intersecteds[x][0].const[1]) - easyatan(lines_of_intersecteds[x][1].const[1]) )
            if x != 0 and x != len(self.dots)-1: angles[x] = math.pi-angles[x]

        self.angles,self.name = angles,name
        
        self.polygonStyleOrdered_ids = order_dots_polygonStyle_by_intersecteds_andReceiveOnlyIds(self.dots,lines_of_intersecteds)

        angle_vision = [Coordinate((0,0)) for c in range(0,len(self.dots))]
        for x in range(0,len(self.dots)):
            dot_id = self.polygonStyleOrdered_ids.index(x)
            dot_id = np.array([dot_id-1,dot_id,dot_id+1])%len(self.dots)
            b1 = self.bisector(dot_id[0],dot_id[1],dot_id[2])
            dot_id = np.array([dot_id[1],dot_id[2],dot_id[0]])
            b2 = self.bisector(dot_id[0],dot_id[1],dot_id[2])
            incenter = Function.intersect(b1,b2)
            
            angle_vision[x] = (incenter-self.dots[x].coord)/3
            #angle_vision[x] = angle_vision[x]/(angle_vision[x].length())
            #direction = -1 if incenter.x < self.dots[x].coord.x else 1
            #angle_vision[x] = Coordinate((b1.dx_by_vectorsize(1),Function.deriative(b1).f(b1.dx_by_vectorsize(1))))*direction
        self.angle_vision = angle_vision
    
    def allIncenters(self):
        incenter_dots = []
        for x in range(0,len(self.dots)):
            dot_id = self.polygonStyleOrdered_ids.index(x)
            dot_id = np.array([dot_id-1,dot_id,dot_id+1])%len(self.dots)
            b1 = self.bisector(dot_id[0],dot_id[1],dot_id[2])
            dot_id = np.array([dot_id[1],dot_id[2],dot_id[0]])
            b2 = self.bisector(dot_id[0],dot_id[1],dot_id[2])
            incenter = Function.intersect(b1,b2)

            incenter_dots.append(Dot(incenter,self.name+"'sPrivateIncenterOf"+self.dots[dot_id[0]].name+self.dots[dot_id[1]].name+self.dots[dot_id[2]].name))
        return incenter_dots
    
    def bisector(self,dot1_id, angle_dot_id, dot2_id,name=None):
        dot_id = order_dots_by_OutAngleRule([self.dots[dot1_id],self.dots[angle_dot_id],self.dots[dot2_id]])[0].index(self.dots[angle_dot_id])
        angle_of_bisector = (easyatan((self.dots[dot1_id].coord-self.dots[angle_dot_id].coord).slope()) + easyatan((self.dots[dot2_id].coord-self.dots[angle_dot_id].coord).slope()))/2
        k1 = math.tan(angle_of_bisector)

        if dot_id != 0 and dot_id != 2: k1 = -1/k1

        k0 = self.dots[angle_dot_id].coord.y-k1*self.dots[angle_dot_id].coord.x

        if name == None:name = self.name+"'sBisectorOf "+self.dots[angle_dot_id].name
        return Function([k0,k1],name)

    def bisector_by_lines(self, dot, lines_of_intersect, dot_id):
        angle_of_bisector = (easyatan(lines_of_intersect[0].const[1]) + easyatan(lines_of_intersect[1].const[1]))/2
        k1 = math.tan(angle_of_bisector)
        if dot_id != 0 and dot_id != len(self.dots)-1: k1 = -1/k1

        k0 = dot.coord.y-k1*dot.coord.x
        return Function([k0,k1],"bisectorOf"+str(dot.name))
    
    def __getitem__(self,dot_name):
        for dot in self.dots:
            if dot.name == dot_name: return dot
        return Dot((0,0),"NULL")

    def getdotid(self,dot_name):
        for c in range(0,len(self.dots)):
            if self.dots[c].name == dot_name: return c
        return -1

    def polygon_name(self):
        name = ""
        for andot in self.polygonStyleOrdered_ids:
            name+=self.dots[andot].name
        return name




class Triangle(Polygon):
    def __init__(self, dots : list[Dot],lines_of_intersecteds,name):
        if len(dots) != 3 : print("For defining a Triangle, you should set 3 dots on there... I'm defining an polygon for you but be careful.")
        Polygon.__init__(self,dots,lines_of_intersecteds,name)
    
    def incenter_coordinate(self):
        self.angle_vision[0]
        self.dots[0]
        line1, line2 = Function.dotsToLine(self.dots[0],self.angle_vision[0]),Function.dotsToLine(self.dots[1],self.angle_vision[1])
        return Function.intersect(line1,line2)
    
    def median_line(self,dot_id,name = None):
        other_dots = [0,1,2]
        other_dots.remove(dot_id)
        median_coord = (self.dots[other_dots[0]].coord+self.dots[other_dots[1]].coord)/2
        if name == None:name = self.name+"'sMedianOf"+self.dots[dot_id].name
        return Function.coordsToLine(self.dots[dot_id].coord,median_coord,name)
    
    def prependicular_line(self,dot_id,name=None):
        other_dots = [0,1,2]
        other_dots.remove(dot_id)
        k = (self.dots[other_dots[0]].coord-self.dots[other_dots[1]].coord).slope()
        k = -1/k # for being prependicular
        c = self.dots[dot_id].coord.y-k*self.dots[dot_id].coord.x

        if name == None: name = self.name+"'sPrependicularOf"+self.dots[dot_id].name
        return Function([c,k],name)

    def line_lengths(self,dot_id):
        other_dots = [0,1,2]
        other_dots.remove(dot_id)
        return Dot.distance_of_points(self.dots[other_dots[0]],self.dots[other_dots[1]])
        
    
    def area(self):
        return self.line_lengths(0)*self.line_lengths(1)*math.sin(self.angles[2])*(1/2)
        
class Angle:
    def bisector(self,dot1_id, angle_dot_id, dot2_id):
        dot_id = self.dots.index(self.dots[angle_dot_id])
        angle_of_bisector = (easyatan((self.dots[dot1_id].coord-self.dots[angle_dot_id].coord).slope()) + easyatan((self.dots[dot2_id].coord-self.dots[angle_dot_id].coord).slope()))/2
        k1 = math.tan(angle_of_bisector)

        if dot_id != 0 and dot_id != len(self.dots)-1: k1 = -1/k1

        k0 = self.dots[angle_dot_id].coord.y-k1*self.dots[angle_dot_id].coord.x

        return Function([k0,k1])
    
    def __init__(self, dots : list[Dot],lines_of_intersected : list[Function],name):
        self.dots,lines_of_intersected = order_dots_by_OutAngleRule(dots,lines_of_intersected)
        angle_id = self.dots.index(dots)
        other_dots = [0,1,2].remove(angle_id)
        angle = abs( easyatan( (dots[angle_id].coord-dots[other_dots[0]].coord).slope() ) - easyatan( (dots[angle_id].coord-dots[other_dots[1]].coord).slope() ) )
        if angle_id != 0 and angle_id != len(self.dots)-1: angle = math.pi-angle

        bisector_line = self.bisector(other_dots[0],angle_id,other_dots[1])
        dx = bisector_line.dx_by_vectorsize(1)
        angle_vision = Coordinate(dx,dx*bisector_line.const[1])

        self.angle = angle
        self.angle_vision = angle_vision
        self.name = name


# free things. damn
def freePolygon(name,dots,it_is_triangle=False): # should get dots in polygon order
    lines_of_intersecteds = []
    for i in range(0,len(dots)):
        f1 = Function.dotsToLine(dots[(i-1)%len(dots)],dots[(i)%len(dots)],dots[(i-1)%len(dots)].name+dots[(i)%len(dots)].name)
        f2 = Function.dotsToLine(dots[(i)%len(dots)],dots[(i+1)%len(dots)],dots[(i)%len(dots)].name+dots[(i+1)%len(dots)].name)
        lines_of_intersecteds.append((f1,f2))
    if it_is_triangle: return Triangle(dots,lines_of_intersecteds,name)
    else: return Polygon(dots,lines_of_intersecteds,name)


class Plane:
    @staticmethod
    def minimumRange(dots : list[Dot]):
        from .support import maxminCoordinates
        minCoord, maxCoord = Coordinate(dots[0].coord.getArrayLike()), Coordinate(dots[0].coord.getArrayLike())
        for dot in dots:
            if dot.coord.x < minCoord.x: minCoord.x = dot.coord.x
            if dot.coord.y < minCoord.y : minCoord.y = dot.coord.y
            if dot.coord.x > maxCoord.x : maxCoord.x = dot.coord.x
            if dot.coord.y > maxCoord.y : maxCoord.y = dot.coord.y
        return maxminCoordinates(minCoord,maxCoord)

    def __init__(self):
        self.dots,self.lines,self.angles,self.polygons = [],[],[],[] # dots, lines, angles, polygons
        self.intersect_lines = []

    def control_linedup(self):
        pass # if all dots in almostly same line

    def control_beuty(self):
        for polygon in self.polygons:
            for angle in polygon.angles:
                if angle > 0.8*math.pi: return False
        return True
    
    def add_object(self,*new_objects):
        for new_object in new_objects:
            if type(new_object) == Dot: 
                self.dots.append(new_object)
                self.intersect_lines.append(None)
            elif type(new_object) == Function: self.lines.append(new_object)
            elif type(new_object) == Angle: self.angles.append(new_object)
            elif type(new_object) == Polygon: self.polygons.append(new_object)
    
    def create_parallel_line(self,name,another_line,c_range = (-10, 10)):
        self.lines.append(Function.random_line_parallelto_(self.lines[self.find_object_by_name_(another_line,Function)],name,c_range))

    def create_beuty_random_line(self,name,c_range=(-10,10),k=None,c=None):
        if c == None: c = c_range[0] + random()*(c_range[1]-c_range[0])

        if k==None and len(self.lines) == 0:
            k = math.tan(random()*math.pi)
            self.lines.append(Function([c,k],name))
        elif k== None:
            anglesum = 0
            for line in self.lines:
                anglesum += easyatan(line.const[1])
            anglesum = (anglesum/len(self.lines))%math.pi
            nlineangle = (random()-0.5)*2*(math.pi/6)+(math.pi-anglesum)
            k = math.tan(nlineangle)
            cvals = [line.const[0] for line in self.lines]
            cavr = sum(cvals)/len(cvals)
            kvals = [easyatan(line.const[1]) for line in self.lines]+[easyatan(k)]
            stdv = avrdistance(kvals,sum(kvals)/len(kvals))
            dist = fixdistance(c,cavr,stdv,constant=stdv)

            rint = int(random()>0.5)
            c = cavr + dist*rint + dist*(rint-1)
            self.lines.append(Function([c,k],name))
        else:
            self.lines.append(Function([c,k],name))

    
    def find_object_by_name_(self, name, object_type):
        if object_type == Function:
            for c in range(0,len(self.lines)):
                if self.lines[c].name == name: return c
        elif object_type == Dot:
            for c in range(0,len(self.dots)):
                if self.dots[c].name == name: return c
        elif object_type == Polygon:
            for c in range(0,len(self.polygons)):
                if self.polygons[c].name == name: return c
        
        return None
    
    def intersect_and_set(self,line_id1,line_id2,name,visibility=True):
        if type(line_id1) == str: line_id1 = self.find_object_by_name_(line_id1,Function)
        if type(line_id2) == str: line_id2 = self.find_object_by_name_(line_id2,Function)

        coord = Function.intersect(self.lines[line_id1],self.lines[line_id2])
        self.dots.append(Dot(coord,name,visibility))
        self.intersect_lines.append([line_id1,line_id2])
    
    def define_polygon_(self, polygon_name,it_is_triangle = False, *dotnames):
        intersected_lines = []
        dots = []
        for dotname in dotnames:
            dot_id = self.find_object_by_name_(dotname, Dot)
            if dot_id == None: 
                print("Dot named '",dotname,"' not found.") ; return
            intersection = self.intersect_lines[dot_id]
            if intersection == None:
                print("Intersected lines required.") ; return
            intersected_lines.append((self.lines[intersection[0]],self.lines[intersection[1]]))
            dots.append(self.dots[dot_id])
        if it_is_triangle: self.polygons.append(Triangle(dots,intersected_lines,polygon_name))
        else : self.polygons.append(Polygon(dots,intersected_lines,polygon_name))
    
    def define_freepolygon_(self,polygon_name,it_is_triangle=False,*dotnames):
        dots = []
        for dotname in dotnames:
            dot_id = self.find_object_by_name_(dotname, Dot)
            if dot_id == None: 
                print("Dot named '",dotname,"' not found.") ; return
            dots.append(self.dots[dot_id])
        self.polygons.append(freePolygon(polygon_name,dots,it_is_triangle=it_is_triangle))

    def clear(self):
        self = self.__init__()
    
    def to_graph(self,graph_step = 0.1):
        xr = np.arange(-10,10,graph_step)
        if len(self.dots) > 0:
            maxminRange = Plane.minimumRange(self.dots)
            xr = np.arange(maxminRange.x.min-graph_step,maxminRange.x.max+graph_step,graph_step)
        
        fig,ax = plt.subplots()
        for line in self.lines : 
            ax.plot(xr,line.f_numpy(xr))
        
        for dot in self.dots : 
            ax.annotate(dot.name,dot.coord.getArrayLike())
            ax.plot(dot.coord.x,dot.coord.y, "r.")
        
        for polygon in self.polygons:
            for i in range(0,len(polygon.dots)):
                ax.annotate( str(float('%.2f' % (polygon.angles[i]*180/math.pi))),(polygon.dots[i].coord + polygon.angle_vision[i]).getArrayLike() )
        
        for angle in self.angles:
            ax.annotate( str(float('%.2f' % (angle.angle*180/math.pi))),(angle.dots[1].coord + angle.angle_vision).getArrayLike() )
        
        plt.show()

    def __str__(self):
        dot_string = "Dots:"+str([str(dot) for dot in self.dots])
        line_string = "Lines:"+str([str(line) for line in self.lines])
        polygon_string = "Polygons"+str([str(polygon) for polygon in self.polygons])
        return dot_string+"\n"+line_string+"\n"+polygon_string
