import robot, threading, time, math

R = robot.Robot()

R.gpio[0].mode = robot.INPUT
R.camera.res = (640, 480)

R.gpio[1].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[1].digital = True  

# Distances and angles travelled in 1 second with 100 power 
# At 100% power for 1 second the robot moves 180 degrees or 0.3 meters
defDistance = 0.26
defAngle = 180

xy = [0, 0]
innerAngle = 0

zero = time.time()
frame = 50 #ms

clear = "scan"

landmarks = []
length = 8
for i in range(length - 1):
    landmarks.append([( i + 1)/2, length])
for i in range(length - 1):
    landmarks.append([length, (length - i - 1)/2])
for i in range(length - 1):
    landmarks.append([(length - i - 1)/2, 0])
for i in range(length - 1):
    landmarks.append([0, (i + 1)/2])

frontProxTimeout = 5.0

tasks = {
    "wheels" : ["panic()", 10**100, "wheels"],
    "proximity" : ["front_prox_timeout()", 5, "proximity"]
}

def queue(task, sleep, tag, overwrite = False):
    if overwrite or tasks[tag][1] == 10**100:
        tasks[tag] = [task, time.time() - zero + sleep, tag]
    

def snap(x, y):
    x -= xy[0]
    y -= xy[1]
    dist = math.sqrt(x**2 + y**2)
    angle = math.degrees(math.asin(y/dist))
    polar(dist, angle)

def polar(distance = 0, angle = 0, marker = 0):
    global xy, innerAngle

    if marker != 0:
        distance = marker.dist
        angle = marker.bearing.y

    turn(angle)
    queue("move({})".format(distance), abs(angle/defAngle), "wheels", True)

def move(dist):
    global xy

    xy[0] += math.cos(innerAngle * dist)
    xy[1] += math.sin(innerAngle * dist)
    R.motors = [-100, -100, 0]
    queue("{}()".format(clear), abs(dist/defDistance), "wheels")

def turn(angle):
    global innerAngle

    sign = angle/abs(angle)
    R.motors = [100 * sign, -100 * sign, 0]
    innerAngle += angle
    queue("{}()".format(clear), abs(angle/defAngle), "wheels")

def check():
    smallesttask = ["", None, ""]
    for task in [*tasks.values()]:
        if smallesttask[1] == None:
            smallesttask = task
            continue
        if task[1] - time.time() + zero < 0 :
            tasks[task[2]][1] = 10**100
            continue
        if task[1] < smallesttask[1]:
                smallesttask = task
    
    if smallesttask[1] < time.time() - zero + frame:
        time.sleep(smallesttask[1] - time.time() + zero)
        eval(smallesttask[0])
        check()

def scan():
    R.motors = [0, 0, 0]

    R.see()
    sheep = R.see()
    
    if sheep == []:
        turn(60)
        return

    elif sheep[0].info.id in range(40):
        print("I see a sheep")
        polar(marker = sheep[0])

def angled(e):
    e.bearing.y
    
def trianglulate():
    global xy, innerAngle
    while len(i for i in R.see().info.id if i in range(100, 123)) <= 2:
        turn(60)
    wall = R.see().sort(key = angled)
    bigger = [wall[0].bearing.y, wall[0].dist]
    smaller = [wall[1].bearing.y, wall[1].dist]
    pos = landmarks[wall[0].info.id - 100]
    distance = math.sqrt((pos[0] - landmarks[wall[0].info.id - 100][0])**2 + (pos[1] - landmarks[wall[0].info.id - 100][1])**2)
    angle = math.asin(math.sin(bigger[0] - smaller[0])/ distance * smaller[1])
    dist = wall[0].dist
    xy = [math.cos(angle) * dist - pos[0], math.sin(angle) * dist - pos[1]]
    innerAngle = bigger[0] + angle

def panic():
    while True:
        print("How did we get here")

def front_prox_timeout():
    global front_prox, seen_front_prox

    front_prox = False
    seen_front_prox = False
    queue("front_prox_timeout()", frontProxTimeout, "proximity")




front_prox = False
seen_front_prox = False
def front_prox_loop():
    global front_prox
    global seen_front_prox
    while True:
        if not front_prox:
            if not R.gpio[0].digital:
                time.sleep(0.5)
                if not R.gpio[0].digital:
                    front_prox = True
                    seen_front_prox = False
                    threading.Thread(target=front_prox_timeout).start()
        else:
            if R.gpio[0].digital:
                if seen_front_prox:
                    front_prox = False
threading.Thread(target=front_prox_loop).start()



def collect_sequence():
    R.motors[0] = 0
    R.motors[1] = 0
    #arm servos
    print("[LOG] collecting sheep")
    time.sleep(2000)
    #if sensor in hopper crossed then return true else return false
    return False

def go_to_pen():
    primarymarkerid = ""
    inpen = False
    atedge = False
    while not inpen:
        if not atedge:
            if not check_front_prx():
                markers = R.see()
                for markeridx in range(len(markers)):
                    print(markers[markeridx].info.type)

                    if markers[markeridx].info.type == robot.MARKER_OWNER.ARENA:#only if part of arena (not if home zone)
                        if markers[markeridx].info.owner:

                            if primarymarkerid == "" or not primarymarkerid in markers:
                                primarymarkerid = markers[0].info.id
                                print(markers[0].info.id)

                            #point towards marker with primarymarkerid and move motors

                        else:
                            search_step()
            else:
                print("reached edge")
                atedge = True
        else:
            #rotate 180 and move foward until tape crossed
            #dump
            pass


def inmarkers(markers, currentmkrid):
    inmarkers = False
    for marker in markers:
        if marker.info.id == currentmkrid:
            inmarkers = True
    return inmarkers


    
     
collected = 0
while True:
    if collected < 3:
        currentmkrid = ""
        markers = R.see()
        if len(markers) > 0:
            for markeridx in range(len(markers)):

                if markers[markeridx].info.type == robot.MARKER_TYPE.SHEEP:
                    if markers[markeridx].info.owner:
                        print("[LOG] found a sheep and we own it")
                        
                        if gotocube(markers[markeridx].info.id):

                            if collect_sequence():
                                collected += 1

                        else:
                            print("[LOG] lost sheep")
                    else:
                        print("[LOG] found a sheep but we dont own it")
        else:
            search_step()
            
    else:
        print("[LOG] going to pen to empty")
        go_to_pen()



        


