import robot, time, math
from operator import itemgetter

R = robot.Robot()

R.gpio[1].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[1].digital = True  

# Distances and angles travelled in 1 second with 100 power 
# At 100% power for 1 second the robot moves 180 degrees or 0.3 meters
defDistance = 0.26
defAngle = 180

zero = time.time()
frame = 50 #ms

frontProxTimeout = 5

tasks = {
    "wheels" : ["panic()", 10**100, "wheels"],
    "proximity" : ["front_prox_timeout()", 5, "proximity"]
}
xy = [0, 0]
innerAngle = 0

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



def queue(task, sleep, tag, overwrite = False):
    if overwrite or tasks[tag][0] == "panic()":
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
    queue("scan()", abs(dist/defDistance), "wheels")

def turn(angle):
    global innerAngle

    sign = angle/abs(angle)
    R.motors = [100 * sign, -100 * sign, 0]
    innerAngle += angle
    queue("scan()", abs(angle/defAngle), "wheels")

def timeStamp(e):
    return e[0]

def check():
    smallesttask = ["", None, ""]
    for task in [*tasks.values()]:
        if smallesttask[1] == None:
            smallesttask = task
            continue
        if task[1] < smallesttask[1]:
                smallesttask = task
    
    if smallesttask[1] < time.time() - zero + frame:
        time.sleep(smallesttask[1] - time.time() + zero)
        eval(smallesttask[0])
        tasks[smallesttask[2]] = ["panic()", 10**100, smallesttask[2]]
        check()

def scan():
    R.motors = [0, 0, 0]

    R.see()
    sheep = R.see()
    
    if sheep == []:
        turn(60)

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
    time.sleep(frontProxTimeout)

    front_prox = False
    seen_front_prox = False

while True:
    time.sleep(frame/1000)

    check()

    queue("scan()", 0, "wheels")
        
    

