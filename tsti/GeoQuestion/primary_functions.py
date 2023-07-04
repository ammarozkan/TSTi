import math

easyatan = lambda theta : math.pi-math.atan(theta*-1) if theta < 0 else math.atan(theta)
    
def order_dots_by_OutAngleRule(dots,*connected_array):
    ordered = False
    while not ordered:
        for c in range(1,len(dots)):
            if dots[c].coord.y > dots[c-1].coord.y or (dots[c].coord.y == dots[c-1].coord.y and dots[c].coord.x > dots[c-1].coord.x):
                ordered = False
                ddrd = dots[c]
                dots[c] = dots[c-1]
                dots[c-1] = ddrd
                

                for i in range(0,len(connected_array)):
                    ddrd = connected_array[i][c]
                    connected_array[i][c] = connected_array[i][c-1]
                    connected_array[i][c-1] = ddrd
            else: ordered = True
    if connected_array != None: 
        result = (dots,)
        for connected in connected_array:
            result = result+(connected,)
        return result
    else: return dots

def getClosestDot(main_dot,dots,return_type,not_that = None):
    distance = lambda dot1,dot2 : math.sqrt((dot1.coord.x-dot2.coord.x)**2 + (dot1.coord.y-dot2.coord.y)**2)
    dots.remove(main_dot)

    if not_that != None :
        if type(not_that) == int: dots.pop(not_that)
        else : dots.remove(not_that)
    closest_distance, closest_dot = distance(main_dot,[dots[0]]), 0
    
    for i in range(0,len(dots)):
        new_distance = distance(main_dot,dots[i])
        if new_distance < closest_distance: 
            closest_distance = new_distance
            closest_dot = i
    
    if type(return_type)  == int: return closest_dot
    else: return dots[closest_dot]
        
        
    

def order_dots_polygonStyle_by_distance(dots,*connected_arrays):
    cId = getClosestDot(dots[0],dots,int)
    ordered_dots = [dots[0],dots[cId]]
    ordered_connecteds = [[connected_array[0],connected_array[cId]] for connected_array in connected_arrays]

    while len(ordered_dots) != dots:
        cId = getClosestDot(ordered_dots[len(ordered_dots)-1],dots,not_that=len(ordered_dots)-2)
        ordered_dots.append(dots[cId])
        for i in range(0,len(ordered_connecteds)):
            ordered_connecteds[i].append(connected_arrays[i][cId])
    
    return (dots,)+tuple(connected_arrays)


def order_dots_polygonStyle_by_intersecteds(dots,lines_of_intersecteds,*connected_arrays):
    def find_another_dot(present_dot,intersected_line):
        for i in range(0,len(lines_of_intersecteds)):
            if intersected_line in lines_of_intersecteds[i] and i != present_dot:
                return i, lines_of_intersecteds[i][int(not bool(lines_of_intersecteds[i].index(intersected_line)))]
        return (-1,-1)

    ordered_dots = []
    ordered_connecteds = [[] for connected_array in connected_arrays]

    next_counter, intersected_line = find_another_dot(-1,lines_of_intersecteds[0][0])

    while len(ordered_dots) != len(dots):
        ordered_dots.append(dots[next_counter])
        for i in range(0,len(ordered_connecteds)): ordered_connecteds[i].append(connected_arrays[i][next_counter])
        next_counter,intersected_line = find_another_dot(next_counter,intersected_line)
    
    return (ordered_dots,)+tuple(connected_arrays)

def order_dots_polygonStyle_by_intersecteds_andReceiveOnlyIds(dots,lines_of_intersecteds):
    def find_another_dot(present_dot,intersected_line):
        for i in range(0,len(lines_of_intersecteds)):
            zero = lines_of_intersecteds[i][0].name == intersected_line.name
            one = lines_of_intersecteds[i][1].name == intersected_line.name
            if (zero or one) and i != present_dot:
                return i, lines_of_intersecteds[i][1 if zero else 0]
        return (-1,-1)

    ordered_ids = []

    next_counter, intersected_line = find_another_dot(-1,lines_of_intersecteds[0][0])

    while len(ordered_ids) != len(dots):
        ordered_ids.append(next_counter)
        next_counter,intersected_line = find_another_dot(next_counter,intersected_line)
    
    return ordered_ids




def select_from_(array, condition, *connected_array): # if condition returns true, I will add the element!
    new_array = []
    result_connected_arrays = ()
    if connected_array != None: 
        for connected in connected_array: result_connected_arrays = result_connected_arrays + ([],)
    else : connected_array = []
    
    for counter in range(0,len(array)):
        if condition(array[counter]): new_array.append(array[counter])
        for connected_counter in range(0,len(connected_array)): result_connected_arrays[connected_counter].append(connected_array[connected_counter][counter])
    
    if connected_array == []: return new_array
    else : return (new_array,)+result_connected_arrays




def avarage(lst):
    sum(lst)/len(lst)

def avrdistance(lst,avr):
    a = 0
    for i in lst:
        a+=abs(i-avr)
    return a/len(lst)

def std_dev(lst,avr):
    a = 0
    for i in lst:
        a+=(i-avr)**2
    return math.sqrt(a/len(lst))

def fixval(x,avr,stdv,constant): # when stdv, standart deviation, goes infinite, the value goes to avarage
    # x is generated value.
    # avr is avarage.
    # stdv is standart deviation of values
    # we want x gets close if stdv is big. and so stdv will not increase somemoment
    return ((stdv**constant)*avr+x)/((stdv**constant)+1)
    # Im using this for getting a value for when angles more different from each other, the c constant should be more similar to each other.

def fixdistance(x,avr,stdv,constant):

    return (stdv*stdv+abs(avr-x))/(stdv+1)
    # Im using this for getting a value for when angles more different from each other, the c constant should be more similar to each other.