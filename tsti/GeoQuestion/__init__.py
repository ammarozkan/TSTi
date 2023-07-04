import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import random as rnd

from .variables import Coordinate, Triangle,order_dots_by_OutAngleRule,Dot,Polygon,Function,Plane
from .language_center import GeometricLanguager
from .imager import GeometricImager,VariableTextor
from .supportfunctions import NE6, formula_NE6, extractfromdots,formula_NE1_fixed,NE1_fixed

def TestLibrary():
    our_plane = Plane()

    our_plane.add_object( Function([0,4],"d1"),Function([0,-0.25],"d3"))
    our_plane.add_object( Function([-4,4],"d2"),Function([-1,-0.25],"d4"))

    our_plane.intersect_and_set("d1","d3","A")
    our_plane.intersect_and_set("d2","d4","B")
    our_plane.intersect_and_set("d1","d4","C")
    our_plane.intersect_and_set("d2","d3","D")
    our_plane.define_polygon_("Patates Cipsi",False,"A","B","C","D")
    #our_plane.add_object(our_plane.polygons[0].bisector(1,2,3))
    our_plane.add_object(*our_plane.polygons[0].allIncenters())




    our_plane.to_graph()
    imager = GeometricImager()
    imager.Draw(our_plane).show()
    
    
