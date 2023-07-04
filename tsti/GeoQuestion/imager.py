from PIL import Image, ImageDraw, ImageFont
from .variables import Plane
from math import sqrt,pi
from .language_center import VariableTextor
import random


DEF_LINECOLOR = (255,0,0)
DEF_DOTCOLOR = DEF_LINECOLOR
DEF_TEXTCOLOR = (255,255,255)
DEF_BCKR = (0,0,0)

class GeometricImager:
    def __init__(self,w=800,h=600,dotSize=5,fontSize=16,lineWidth=5,variableMargin=(0,0),rangec=(20,20),spacesBetweenVariables=2,roundToDigits=-1,modifyToRealistic=False,onesizeAnglePos=True,anglei_distance=None,line_color=DEF_LINECOLOR,dot_color=DEF_DOTCOLOR,text_color=DEF_TEXTCOLOR,background_color=DEF_BCKR,font_name="Hack-Regular.ttf"):
        if anglei_distance == None: anglei_distance = sqrt(w**2+h**2)/50

        self.w,self.h,self.dotSize,self.fontSize,self.lineWidth = w,h,dotSize,fontSize,lineWidth
        self.variableMargin, self.spacesBetweenVariables,self.roundToDigits = variableMargin, spacesBetweenVariables, roundToDigits
        self.modifyToRealistic,self.onesizeAnglePos,self.anglei_distance = modifyToRealistic,onesizeAnglePos,anglei_distance
        self.line_color,self.dot_color,self.text_color,self.background_color = line_color,dot_color,text_color,background_color
        self.font_name = font_name

        self.xrangec, self.yrangec = rangec[0],rangec[1]

        self.colors = [(238, 164, 127),(251, 234, 235),(204, 243, 129)]

    def Draw(self,plane,title="",print_angles=True,debugmode=False):
        img = Image.new("RGB",(self.w,self.h),self.background_color)
        drawer = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_name,self.fontSize)

        dotRange = Plane.minimumRange(plane.dots)
        if self.modifyToRealistic:
            rangeShould = max(dotRange.x.max-dotRange.x.min, dotRange.y.max-dotRange.y.min)
            xmid = (dotRange.x.max+dotRange.x.min)/2
            ymid = (dotRange.y.max+dotRange.y.min)/2

            dotRange.x.max = xmid+rangeShould/2
            dotRange.x.min = xmid-rangeShould/2
            dotRange.y.max = ymid+rangeShould/2
            dotRange.y.min = ymid-rangeShould/2

        xrange = (dotRange.x.max - dotRange.x.min)
        yrange = (dotRange.y.max - dotRange.y.min)
        dotRange.x.max += xrange/self.xrangec
        dotRange.x.min -= xrange/self.xrangec
        dotRange.y.max += yrange/self.yrangec
        dotRange.y.min -= yrange/self.yrangec

        xi = lambda x: (x - dotRange.x.min)*self.w/(dotRange.x.max - dotRange.x.min)
        yi = lambda y: (y - dotRange.y.min)*self.h/(dotRange.y.max - dotRange.y.min)

        if not debugmode:
            for polygon in plane.polygons:
                coordinates = [(xi(polygon.dots[dId].coord.x),yi(polygon.dots[dId].coord.y)) for dId in polygon.polygonStyleOrdered_ids]
                drawer.polygon(coordinates,fill = (self.colors.pop(random.randint(0,len(self.colors)-1))))
                for i in range(0,len(coordinates)):
                    c1 = coordinates[i]
                    c2 = coordinates[(i+1)%len(coordinates)]
                    drawer.line([c1,c2],fill=(0,0,0),width=self.lineWidth)


        else:
            for line in plane.lines:
                ymin, ymax = line.f(dotRange.x.min), line.f(dotRange.x.max)
                drawer.line([(0,yi(ymin)),(self.w,yi(ymax))], fill=self.line_color, width = self.lineWidth)

        for dot in plane.dots:
            if dot.visibility == False:continue
            x,y = xi(dot.coord.x), yi(dot.coord.y)
            start = (x-self.dotSize,y-self.dotSize)
            stop = (x+self.dotSize,y+self.dotSize)
            drawer.ellipse([start,stop],fill=self.dot_color)
            drawer.text((x,y-2),dot.name,fill=self.text_color,font=font)

        if print_angles == True and debugmode == True:
            for polygon in plane.polygons:
                for i in range(0,len(polygon.dots)):
                    x,y = None,None
                    if self.onesizeAnglePos:
                        avy = polygon.angle_vision[i].y*(xrange/yrange)
                        avx = polygon.angle_vision[i].x
                        avx, avy = avx/sqrt(avx**2+avy**2),avy/sqrt(avx**2+avy**2)
                        x = xi(polygon.dots[i].coord.x) + self.anglei_distance*avx
                        y = yi(polygon.dots[i].coord.y) + self.anglei_distance*avy
                    else:
                        x = xi(polygon.dots[i].coord.x + polygon.angle_vision[i].x)
                        y = yi(polygon.dots[i].coord.y + polygon.angle_vision[i].y)

                    slope = abs(polygon.angle_vision[i].y/polygon.angle_vision[i].x)
                    anglestring = "{:.2f}".format(polygon.angles[i]*180/pi)
                    x -= (self.fontSize*12/16)*len(anglestring)/2
                    y -= (self.fontSize*12/16)/2
                    drawer.text((x,y),anglestring,fill=self.text_color,font=font)

        drawer.text((10,10),title,fill=self.text_color,font=font)

        return img

    def DrawWithVariables(self,plane,variables,title=""):
        geo_img = self.Draw(plane,title,False)
        visible_var_count = variables["^visible_count"]
        h_character = self.fontSize

        sizex = self.w
        sizey = visible_var_count*h_character+self.variableMargin[1]*2+self.spacesBetweenVariables*(visible_var_count-1)

        variable_image = Image.new("RGB",(sizex,sizey),self.background_color)

        drawer = ImageDraw.Draw(variable_image)
        font = ImageFont.truetype(self.font_name,self.fontSize)

        vt = VariableTextor(roundToDigits=self.roundToDigits)

        counter = 0
        for varname in variables:
            if varname == "^visible_count" or variables[varname]["visibility"] != True:continue
            varstring = vt.textit(variables[varname])

            x = self.variableMargin[0]
            y = self.variableMargin[1]+counter*(h_character+self.spacesBetweenVariables)
            drawer.text((x,y),varstring,fill=self.text_color,font=font)
            counter += 1

        merged = Image.new("RGB",(self.w,self.h+variable_image.size[1]))
        merged.paste(geo_img,(0,0))
        merged.paste(variable_image,(0,self.h))

        return merged
