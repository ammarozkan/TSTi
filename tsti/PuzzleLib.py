import random
import json

    #Squaret2
class Squaret2:
    def __init__(self,size):
        self.base = [ [0 for y in range(size)] for x in range(size)]
        self.size = size
    
    def calculateBasic(self,basic, d,k, limit = 10):
        for x in range(self.size):
            for y in range(self.size):
                self.base[x][y] = (basic+x*d+y*k)%limit
    
    def calculateExtra(self,d,k, limit=10):
        for x in range(self.size):
            for y in range(self.size):
                if x >= 1:
                    self.base[x][y] = (self.base[x][y]+self.base[x-1][y]*d)%limit
                if y >= 1:
                    self.base[x][y] = (self.base[x][y]+self.base[x][y-1]*k)%limit
    
    def addZippy(self, x, y, xz, yz, d):
        if x+xz >= self.size or y+yz >= self.size or x+xz < 0 or y+yz < 0 or xz == 0 or yz == 0:
            return self.base[x][y]
        else:
            return self.base[x][y]+self.addZippy(x+xz,y+yz,xz,yz,d)*d
    
    def calculateZippy(self, xz, yz, d,limit=10):
        for x in range(self.size):
            for y in range(self.size):
                self.base[x][y] = (self.addZippy(x,y,xz,yz,d))%limit
    
    def calculateZippyReverse(self, xz, yz, d, limit=10):
        for x in range(self.size):
            for y in range(self.size):
                self.base[self.size-x-1][self.size-y-1] = (self.addZippy(self.size-x-1,self.size-y-1,xz,yz,d))%limit

    
    def limitTo(self,what):
        for x in range(self.size):
            for y in range(self.size):
                self.base[x][y] = self.base[x][y]%what

    def randomRule(self):
        return [[random.randrange(0,10),random.randrange(0,3),random.randrange(0,3)],
                [random.randrange(0,3),random.randrange(0,3)],
                [random.randrange(-1,2),random.randrange(-1,2),random.randrange(0,2)],
                [random.randrange(1,4),random.randrange(1,4),random.randrange(0,2)]]

    def randomRuleExtreme(self):
        return [[random.randrange(0,10),random.randrange(1,4),random.randrange(1,4)],
                [random.randrange(1,4),random.randrange(1,4)],
                [random.randrange(-1,2),random.randrange(-1,2),random.randrange(1,3)],
                [random.randrange(-1,2),random.randrange(-1,2),random.randrange(1,3)]]
    
    def calculateRule(self,rule,st_value = None,limit=10):
        if st_value == None: st_value = random.randrange(0,limit)
        self.calculateBasic(st_value,rule[0][1],rule[0][2],limit)
        self.calculateExtra(rule[1][0],rule[1][1],limit)
        self.calculateZippy(rule[2][0],rule[2][1],rule[2][2],limit)
        self.calculateZippyReverse(rule[3][0],rule[3][1],rule[3][2],limit)
    
    def loadfromfile(self,path,nameinfile="dailysquaret2"):
        self.base = json.load(open(path))[nameinfile]
    
    def savetofile(self,path,nameinfile="dailysquaret2"):
        s = json.load(open(path))
        s[nameinfile]=self.base
        print("DDAATTAAAA:",s)
        with open(path,"w") as outfile:
            outfile.write( json.dumps(s, indent=4) )

        