from PIL import Image
import os

scalar = lambda tup,k : tuple([x*k for x in tup])
adder = lambda tup,k : tuple([x+k for x in tup])

def getMaxLengthedElement(arr):
    best = 0
    for a in arr:
        if len(a) > best: best = len(a)
    return best

def coloredL(imgLA,color_1=(0.5,0.5,0.2)): #color_1 should be 0-2
    L,A = imgLA.split()
    img = Image.merge("RGBA", ( L.point(lambda i : i*color_1[0]), L.point(lambda i : i*color_1[1]), L.point(lambda i : i*color_1[2]), A ))
    return img


'''
    arr : the array that generates image from there. 
        [
            [1,2,5] # first line of images
            [1,2,3] # second line of images
            [       # third line of images
                1, # id of an image
                5, # id of an image should be (-1:empty,0:sphere,1:cube,2:triangle or should be defined in the definitions.)
                7,
            ]
        ]
    one_size_of_element : one square image's edge size
    background_color : background color.
    definitions : definition of an id for specific color
    {
        5:[0,(1,0.5,1)] # if id 5 is finded on the array, function will look at definitions firstly. 
            if 5 is defined here, the first indice of 5 will represent image id (basic shapes. told in arr explanation) and second indice will represent color of image. 
            [0,255] range should entered as [0.0,1.0] range
    }
'''
def getArray(arr,one_size_of_element=50,background_color=(255,127,0,255),padding=0,space = (0,0),definitions={}):
    maxlengthelement = getMaxLengthedElement(arr)
    height = len(arr)*one_size_of_element+2*padding+space[1]*(len(arr)-1)
    width = maxlengthelement*one_size_of_element+2*padding+space[0]*(maxlengthelement-1)
    img = Image.new("RGBA",(width,height),color=(120,120,120,0))
    background = Image.new("RGBA",(width,height),color=background_color)

    size = scalar((1,1),one_size_of_element)
    images = [
        Image.open(os.path.dirname(__file__)+"/base_sphere.png").resize(size).convert("LA"), #sphere_base
        Image.open(os.path.dirname(__file__)+"/base_cube.png").crop( (320,0,860,630) ).resize(size).convert("LA"), #cube_base
        Image.open(os.path.dirname(__file__)+"/base_triangle.png").resize(size).convert("LA"), #triangle_base
        Image.open(os.path.dirname(__file__)+"/man1.png").resize(size).convert("LA") #man1_base
    ]
    empty_base = Image.new("LA",size,color=(120,0))

    for y,yElement in enumerate(arr):
        for x,xElement in enumerate(yElement):
            osoe = one_size_of_element
            box = ((osoe+space[0])*x+padding, (osoe+space[1])*y+padding,(osoe+space[0])*x +osoe+padding, (osoe+space[1])*y +osoe+padding)
            #print(box)
            element = definitions[xElement][0] if xElement in definitions else xElement
            color = definitions[xElement][1] if xElement in definitions else (1,1,1)
            CCL = coloredL(images[element] if element != -1 else empty_base,color)
            img.paste(CCL,box)
    
    #background setting sector
    mask = img.split()[3].point(lambda i: i < 25 and 255)
    img.paste(background,None,mask)
    
    return img

def getArrayByText(text,one_size_of_element=50,background_color=(255,127,0,255),padding=0,space = (0,0),definitions={}):
    from ast import literal_eval
    arr = literal_eval(text)
    return getArray(arr,definitions=definitions,one_size_of_element=one_size_of_element,padding=padding,space=space,background_color=background_color)

def randomSet(arr, val, count):
    from random import randint
    rCount = 0
    while rCount != count:
        for y in range(0,len(arr)):
            for x in range(0,len(arr[y])):
                if randint(0,1500) > 1300 and arr[y][x] == -1:
                    rCount += 1
                    arr[y][x] = val
                if rCount == count:
                    return arr
    return arr

def indexSet(arr,val,index,count):
    rCount = 0
    for i in range(0,len(arr[index])):
        arr[index][i] = val
        rCount += 1
        if rCount == count: return arr
    return arr

def getArrayByArrayRule(rule_array,one_size_of_element=50,background_color=(255,127,0,255),padding=0,space = (0,0),definitions={}):
    arr = []
    element_size = (rule_array[0],rule_array[1])
    arr = [ [-1 for x in range(0,element_size[0])] for y in range(0,element_size[1]) ]
    for i in range(2,len(rule_array)):
        if rule_array[i][0] == 'r': arr = randomSet(arr,rule_array[i][1][0],rule_array[i][1][1])
        elif rule_array[i][0] == 'a': arr = indexSet(arr,rule_array[i][1][0],rule_array[i][1][1],rule_array[i][1][2])

    #print("array is :",arr,", for rule :",rule_array)

    return getArray(arr,definitions=definitions,one_size_of_element=one_size_of_element,padding=padding,space=space,background_color=background_color)
    



def getArrayByRule(rule,one_size_of_element=50,background_color=(255,127,0,255),padding=0,space = (0,0),definitions={}):
    arr = []
    element_size = (0,0)
    error = None

    rule = rule.split(" ")
    print("rules:",rule)

    if not rule[0].isdigit() or not rule[1].isdigit(): return None
    else : 
        element_size = (int(rule[0]),int(rule[1]))

    # control state
    puttedCount = 0
    for i in range(2,len(rule)):
        if [rule[i]] != rule[i].split('r'):
            rr = rule[i].split('r')
            if len(rr) != 2 or not rr[0].isdigit() or not rr[1].isdigit():
                print("Failed at ",i,"th prompt. Syntax should be [Type]r[Count] or Type or Count is not digit.")
                return None
            else:
                rr = [int(rr[0]),int(rr[1])]
                puttedCount += rr[1]
        elif [rule[i]] != rule[i].split('a'):
            rr = rule[i].split('a')
            if len(rr) != 2 or len(rr[1].split(',')) != 2:
                print("Failed at ",i,"th prompt. Syntax should be [Type]a[Index],[Count]")
                return None
            else:
                rr[1] = rr[1].split(',')
                if not rr[1][0].isdigit() or not rr[1][1].isdigit():
                    print("Failed at ",i,"th prompt. Index or Count is not digit.")
                    return None
                else:
                    rr = [int(rr[0]),[int(rr[1][0]),int(rr[1][1])]]
                    if rr[1][0] > element_size[1] :
                        print("Failed at ",i,"th prompt. ")
                        print("Index passed Max. Max:",element_size[1]," Index:",rr[1][0])
                        return None
                    elif rr[1][1] > element_size[1]:
                        print("Failed at ",i,"th prompt. ")
                        print("Count passed Max. Max:",element_size[0]," Count:",rr[1][1])
                        return None
                    puttedCount += rr[1][1]
            pass # array rule
    if puttedCount > element_size[0]*element_size[1]:
        print("Failed at putting. Putting count is greater than max count.")
        return None
    
    rule[0],rule[1] = int(rule[0]), int(rule[1])
    for i in range(2,len(rule)):
        if [rule[i]] != rule[i].split('r'):
            rule[i] = rule[i].split('r')
            rule[i] = ['r',[int(rule[i][0]),int(rule[i][1])]]
        elif [rule[i]] != rule[i].split('a'):
            rule[i] = rule[i].split('a')
            rule[i][1] = rule[i][1].split(',')
            rule[i] = ['a',[int(rule[i][0]),int(rule[i][1][0]),int(rule[i][1][1])] ]
            pass # array rule
    print(rule)
    '''

    for i in range(2,len(rule)):
        if [rule[i]] != rule[i].split('r'):
            rr = rule[i].split('r')
            rr = [int(rr[0]),int(rr[1])]
            arr = randomSet(arr,rr[0],rr[1])
            print("Runned rule 'r' for:",rr[0],",",rr[1],".")
        elif [rule[i]] != rule[i].split('a'):
            rr = rule[i].split('a')
            rr[1] = rr[1].split(',')
            rr = [ int(rr[0]),[int(rr[1][0]),int(rr[1][1])] ]
            arr = indexSet(arr,rr[0],rr[1][0],rr[1][1])
            print("Runned rule 'a' for:",rr[0],",",rr[1][0],",",rr[1][1],".")
            pass # array rule
    '''
    return getArrayByArrayRule(rule,definitions=definitions,one_size_of_element=one_size_of_element,padding=padding,space=space,background_color=background_color)
