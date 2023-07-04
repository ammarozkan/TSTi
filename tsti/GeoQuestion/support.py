class valueRange:
    def __init__(self, min,max):
        self.min,self.max = min,max
from .variables import Coordinate

class maxminCoordinates:
    def __init__(self, minC : Coordinate,maxC : Coordinate):
        self.x = valueRange(minC.x,maxC.x)
        self.y = valueRange(minC.y,maxC.y)