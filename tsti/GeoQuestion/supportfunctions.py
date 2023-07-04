import os,json,math
from .variables import *

def dumbdistance(newdata,adata,MMR):
	distance = 0
	for i in range(1,len(newdata)-1):
		distance += abs((100/(MMR[i-1][newdata[0]-3][1]-MMR[i-1][newdata[0]-3][0])) * (newdata[i]-adata[i]))
	return distance

def closestone(thedata,alldatas,MMR):
	dist = dumbdistance(thedata,alldatas[0],MMR)
	result = [alldatas[0]]
	for adata in alldatas:
		ndist = dumbdistance(thedata,adata,MMR)
		if ndist < dist: 
			result = [adata[len(adata)-1]]
			dist = ndist
		elif ndist == dist:
			result.append(adata[len(adata)-1])
	return result,dist

def extractfromdots(Dots):
	AVDOT = Dot.average_of_points(Dots)

	calcus = []
	slopes = []
	slopesrev = []
	distances = []
	for dot1 in Dots:
		for dot2 in Dots:
			if dot1.coord.x != dot2.coord.x and dot1.coord.y != dot2.coord.y and ((dot1.name,dot2.name) not in calcus or (dot2.name,dot1.name) not in calcus): 
				slopes.append(math.atan((dot2.coord.y-dot1.coord.y)/(dot2.coord.x-dot1.coord.x)))
				slopesrev.append(math.atan((dot2.coord.x-dot1.coord.x)/(dot2.coord.y-dot1.coord.y)))
				distances.append(Dot.distance_of_points(dot1,dot2))
			calcus.append((dot1.name,dot2.name))

	xposes = []
	yposes = []
	for dot in Dots:
		xposes.append(dot.coord.x)
		yposes.append(dot.coord.y)

	maxminR = Plane.minimumRange(Dots)

	beuty = std_dev(slopes,sum(slopes)/len(slopes))
	beutyrev = std_dev(slopesrev,sum(slopesrev)/len(slopesrev))
	beutydist = std_dev(distances,sum(distances)/len(distances)) / math.sqrt((maxminR.x.max-maxminR.x.min)**2 + (maxminR.y.max-maxminR.y.min)**2)

	beutyx = std_dev(xposes,sum(xposes)/len(xposes))
	beutyy = std_dev(yposes,sum(yposes)/len(yposes))
	beutydisturbition = beutyy/beutyx
	beutywh = (maxminR.x.max-maxminR.x.min)/(maxminR.y.max-maxminR.y.min)
	centeredmo = math.sqrt((AVDOT.coord.x-(maxminR.x.max+maxminR.x.min)/2)**2 + (AVDOT.coord.y-(maxminR.y.max+maxminR.y.min)/2)**2) / math.sqrt((maxminR.x.max-maxminR.x.min)**2 + (maxminR.y.max-maxminR.y.min)**2)
	return [len(Dots),beuty,beutyrev,beutydist,beutyx,beutyy,beutydisturbition,beutywh,centeredmo]

def formula_NE6(dotcount,beuty,beutyrev,beutydist,beutyx,beutyy,beutydisturbition,beutywh,centeredmo,gooddatas=[]):
	newdata = [dotcount,beuty,beutyrev,beutydist,beutyx,beutyy,beutydisturbition,beutywh,centeredmo]

	# these first and second file should be in GeoQuestion library folder
	# first file : the json file for getting info about value ranges
	g = open(os.path.dirname(__file__)+"/gooddatasranges5.json")
	MMR = json.load(g)["rangearray"]

	# second file : good datas that prooved themself as being goood....
	filename = os.path.dirname(__file__)+"/gooddatasv2.json"
	f = open(filename)
	data = json.load(f)

	gooddatas += data["allgooddatas"]

	res,dist = closestone(newdata,gooddatas,MMR)
	return (True in res and False not in res),dist

def getdataforNE1(Dots):
	calcus = []
	slopes = []
	slopesrev = []
	distances = []
	for dot1 in Dots:
		for dot2 in Dots:
			if dot1.coord.x != dot2.coord.x and dot1.coord.y != dot2.coord.y and ((dot1.name,dot2.name) not in calcus or (dot2.name,dot1.name) not in calcus): 
				slopes.append(math.atan((dot2.coord.y-dot1.coord.y)/(dot2.coord.x-dot1.coord.x)))
				slopesrev.append(math.atan((dot2.coord.x-dot1.coord.x)/(dot2.coord.y-dot1.coord.y)))
				distances.append(Dot.distance_of_points(dot1,dot2))
			calcus.append((dot1.name,dot2.name))

	maxminR = Plane.minimumRange(Dots)

	beuty = std_dev(slopes,sum(slopes)/len(slopes))
	beutyrev = std_dev(slopesrev,sum(slopesrev)/len(slopesrev))
	beutydist = std_dev(distances,sum(distances)/len(distances)) / math.sqrt((maxminR.x.max-maxminR.x.min)**2 + (maxminR.y.max-maxminR.y.min)**2)

	return beuty,beutyrev,beutydist

def formula_NE1_fixed(dotcount,beuty,beutyrev,beutydist,beutyx,beutyy,beutydisturbition,beutywh,centeredmo,gooddatas=[]):
	return (beuty+beutyrev) > 1.50 and beutydist < 0.20 #NE1-FIXED

def NE1_fixed(Dots):
	beuty,beutyrev,beutydist = getdataforNE1(Dots)
	return (beuty+beutyrev) > 1.50 and beutydist < 0.20 #NE1-FIXED

def NE6(Dots,gooddatas=[]):
	return formula_NE6(gooddatas,*extractfromdots(Dots))