import robot, threading, time, math

R = robot.Robot()

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

def tick():
    time.sleep(frame/1000)

reset = "off"

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

tasks = {
    "wheels" : ["panic()", 10**100, "wheels"],
    "proximity" : ["front_prox_timeout()", 5, "proximity"],
}

def queue(task, sleep, tag, overwrite = False):
    if overwrite or tasks[tag][1] == 10**100:
        tasks[tag] = [task, time.time() - zero + sleep, tag]
    return time.time() - zero + sleep

def clear(tag):
    tasks[tag] = ["print(yourmom)", 10**100, tag]

frontProxTimeout = 5

front_prox = False
seen_front_prox = False

def front_prox_timeout():
    global front_prox, seen_front_prox

    front_prox = False
    seen_front_prox = False
    queue("front_prox_timeout()", frontProxTimeout, "proximity")

def front_prox_loop():
    global front_prox, seen_front_prox
    while True:
        if not front_prox and not R.gpio[0].digital:
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

def check_front_prx():
    global front_prox
    global seen_front_prox
    #if not seen_front_prox:
    #    seen_front_prox = True
    return front_prox


def snap(x, y):
    x -= xy[0]
    y -= xy[1]
    dist = math.sqrt(x**2 + y**2)
    angle = math.degrees(math.asin(y/dist))
    return polar(dist, angle)

def polar(distance = 0, angle = 0, marker = 0):
    global xy, innerAngle

    if marker != 0:
        distance = marker.dist
        angle = marker.bearing.y

    turn(angle)
    return queue("move({})".format(distance), abs(angle/defAngle), "wheels", True)

def move(dist):
    global xy

    xy[0] += math.cos(innerAngle * dist)
    xy[1] += math.sin(innerAngle * dist)
    R.motors = [-100, -100, 0]
    queue("{}()".format(reset), abs(dist/defDistance), "wheels")
    return abs(dist/defDistance)

def turn(angle):
    global innerAngle

    sign = angle/abs(angle)
    R.motors = [100 * sign, -100 * sign, 0]
    innerAngle += angle
    queue("{}()".format(reset), abs(angle/defAngle), "wheels")
    return abs(angle/defAngle)

def off():
    R.motors = [0, 0, R.motors[2]]

def angled(e):
    e.bearing.y
    
def trianglulate():
    global xy, innerAngle
    clear("wheels")
    while len(i for i in R.see().info.id if i in range(100, 123)) <= 2:
        turn(60)
        tick()
    wall = R.see().sort(key = angled)
    bigger = [wall[0].bearing.y, wall[0].dist]
    smaller = [wall[1].bearing.y, wall[1].dist]
    pos = landmarks[wall[0].info.id - 100]
    distance = math.sqrt((pos[0] - landmarks[wall[0].info.id - 100][0])**2 + (pos[1] - landmarks[wall[0].info.id - 100][1])**2)
    angle = math.asin(math.sin(bigger[0] - smaller[0])/ distance * smaller[1])
    dist = wall[0].dist
    xy = [math.cos(angle) * dist - pos[0], math.sin(angle) * dist - pos[1]]
    innerAngle = bigger[0] + angle

def scan():
    R.motors = [0, 0, R.motors[2]]

    R.see()
    sheep = R.see()
    
    if sheep == []:
        return turn(60)
        

    elif sheep[0].info.id in range(40):
        #priority code for value
        print("I see a sheep")
        return polar(marker = sheep[0])

def check():
    while True:  
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
        else:
            tick()
        
threading.Thread(target = check).start()   

while not R.gpio[2].input:
    tick()

bucketList = [
    "snap(6, 7)",
    "scan()",
    "snap(6,9)"
]

    
while True:
    timer = eval(bucketList[0])
    while(time.time() - zero < timer):
        tick()
        #if collision detection 
        trianglulate()
        timer = eval(bucketList[0])
    bucketList.pop(0)
    



        
    

