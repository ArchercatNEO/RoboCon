# TODO:
#Collision detection in main loop how???????
#Generalise coordinates in bucvket list
#Finish dropoff()

import robot, threading, time, math

R = robot.Robot()

R.gpio[0].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[0].digital = True  

R.gpio[1].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[1].digital = True  

# Distances and angles travelled in 1 second with 100 power 
# At 100% power for 1 second the robot moves 180 degrees or 0.3 meters
defDistance = 0.26
defAngle = 180
power = 100
defTurnAngle = 60

xy = [0, 0# TODO:
#Collision detection in main loop how???????
#Generalise coordinates in bucvket list
#Finish dropoff()

import robot, threading, time, math

R = robot.Robot()

R.gpio[0].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[0].digital = True  

R.gpio[1].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[1].digital = True  

# Distances and angles travelled in 1 second with 100 power 
# At 100% power for 1 second the robot moves 180 degrees or 0.3 meters
defDistance = 0.26
defAngle = 45
power = 100
defTurnAngle = 60

xy = [0, 0]
innerAngle = 0

enable = True

zero = time.time()
frame = 50 #ms

landmarks = []
length = 6 

for i in range(length):
    landmarks.append([i + 0.5, length])
for i in range(length, 1, -1):
    landmarks.append([length, i - 0.5])
for i in range(length, 1, -1):
    landmarks.append([i - 0.5, 0])
for i in range(length):
    landmarks.append([0, i + 0.5])

big = length * 3/4
small = length/4
center = length/2

nodes = {
    "top-left" : [small, big],
    "top-right" : [2.5, 4.5],
    "bottom-left" : [small, small],
    "bottom-right" : [big, small],
    "top-left-pen" : [center - 0.5, center + 0.5],
    "top-right-pen" : [center + 0.5, center + 0.5],
    "bottom-left-pen" : [center - 0.5, center - 0.5],
    "bottom-right-pen" : [center + 0.5, center - 0.5],
}

cycle = ["top-right", "bottom-right", "bottom-left", "top-left"]
print(cycle)
teams = {
    robot.TEAM.LEON : [0, range(0, 9)],
    robot.TEAM.ZHORA : [1, range(10, 19)],
    robot.TEAM.PRIS : [2, range(20, 29)],
    robot.TEAM.ROY : [3, range(30, 39)]
}

bucketList = []

#for i in range(teams[R.zone][0]):
    #cycle.insert(cycle.pop(len(cycle) - 1)

for i in cycle:
    x = nodes[i][0]
    y = nodes[i][1]
    bucketList.extend(["snap({}, {})".format(x, y), "scan()", "scan()"])


def tick():
    time.sleep(frame/1000)

reset = "off"

tasks = {
    "wheels" : ["panic()", 10**100, "wheels"],
    "servos" : ["panic()", 10**100, "servos"],
}

def queue(task, sleep, tag, overwrite = False):
    if overwrite or tasks[tag][1] == 10**100:
        tasks[tag] = [task, time.time() - zero + sleep, tag]
    return time.time() - zero + sleep

def clear(tag):
    tasks[tag] = ["print(yourmom)", 10**100, tag]

def snap(x, y):
    x -= xy[0]
    y -= xy[1]
    dist = math.sqrt(x**2 + y**2)
    angle = math.degrees(math.asin(y/dist))
    return [polar(dist, angle), "there({}, {})".format(x, y)]

def there(x, y):
    trianglulate()
    return [x, y] == xy    

def polar(distance = 0, angle = 0, marker = 0):
    global xy, innerAngle

    if marker != 0:
        distance = marker.dist
        angle = marker.bearing.y

    turn(angle)
    return queue("move({})".format(distance), abs(angle/defAngle), "wheels", True) + abs(distance/defDistance)

def move(dist):
    global xy
    print("moving {} meters in {} seconds".format(dist, abs(dist/defDistance)))

    xy[0] += math.cos(innerAngle * dist)
    xy[1] += math.sin(innerAngle * dist)
    if enable:
        R.motors[0] = power-7
        R.motors[1] = power + 3.5
    return queue("{}()".format(reset), abs(dist/defDistance), "wheels")

def turn(angle):
    global innerAngle
    print("turning {} degrees in {} seconds".format(angle, abs(angle/defAngle)))

    sign = angle/abs(angle)
    if enable:
        R.motors[0] = (power-7) * sign
        R.motors[1] = -(power + 3.5) * sign
    innerAngle += angle
    return queue("{}()".format(reset), abs(angle/defAngle), "wheels")

def off():
    R.motors[0] = 0
    R.motors[1] = 0
    R.servos[0] = 0

def dropoff():
    R.servos[0] = 100
    queue("off()", 1, "servos")
    
    
def trianglulate():
    global xy, innerAngle
    clear("wheels")
    while len(list(filter(lambda x : x.info.id not in range (100, 123), R.see()))) <= 2:
        turn(defTurnAngle)
        tick()
    wall = R.see().sort(key = lambda z : z.bearing.y)
    bigger = [wall[0].bearing.y, wall[0].dist]
    smaller = [wall[1].bearing.y, wall[1].dist]
    pos_bigger = landmarks[wall[0].info.id - 100]
    pos_smaller = landmarks[wall[1].info.id - 100]
    #the distance between point a and b
    distance = math.sqrt((pos_bigger[0] - pos_smaller[0])**2 + (pos_bigger[1] - pos_smaller[1])**2)
    angle = math.asin(math.sin(bigger[0] - smaller[0])/ distance * smaller[1])
    dist = wall[0].dist
    xy = [math.cos(angle) * dist - pos_bigger[0], math.sin(angle) * dist - pos_bigger[1]]
    innerAngle = 180 - bigger[0] - angle

def scan():
    off()

    R.see()
    time.sleep(0.1)
    tags = R.see()
    sheep = list(filter(lambda tag : tag.info.id in teams[R.zone][1], tags))

    if not sheep:
        return [turn(defTurnAngle), "false()"]
    
    print("I see a sheep")
    return [polar(marker = sheep[0]), True]

def false():
    return False
    



def check():
    while True:
        todo = []
        
        for task in [*tasks.values()]: 
            if task[1] < time.time() - zero + frame/1000: 
                todo.append(task)

        todo.sort(key = lambda task : task[1])
        for task in todo:
            if task[1] > time.time() + zero:
                time.sleep(task[1] - time.time() + zero)
            eval(task[0])
            tasks[task[2]][1] = 10*100
        
        tick()
        
threading.Thread(target = check).start()   
    
while True:
    returned = eval(bucketList[0])
    timer = returned[0]
    while(time.time() - zero < timer):
        tick()
        
        #if collision detection 
        #trianglulate()
        #returned = eval(bucketList[0])
        #timer = returned[0]
    if eval(returned[1]):

        bucketList.pop(0)
    


innerAngle = 0

enable = False

zero = time.time()
frame = 50 #ms

landmarks = []
length = 6 

for i in range(length):
    landmarks.append([i + 0.5, length])
for i in range(length, 1, -1):
    landmarks.append([length, i - 0.5])
for i in range(length, 1, -1):
    landmarks.append([i - 0.5, 0])
for i in range(length):
    landmarks.append([0, i + 0.5])

big = length * 3/4
small = length/4
center = length/2

nodes = {
    "top-left" : [small, big],
    "top-right" : [big, big],
    "bottom-left" : [small, small],
    "bottom-right" : [big, small],
    "top-left-pen" : [center - 0.5, center + 0.5],
    "top-right-pen" : [center + 0.5, center + 0.5],
    "bottom-left-pen" : [center - 0.5, center - 0.5],
    "bottom-right-pen" : [center + 0.5, center - 0.5],
}

cycle = ["top-right", "bottom-right", "bottom-left", "top-left"]
teams = [
    "TEAM.LEON" : [0, range(0, 9)],
    "TEAM.ZHORA":[1, range(10, 19)],
    "TEAM.PRIS":[2, range(20, 29)],
    "TEAM.ROY":[3, range(30, 39)]
]

bucketList = []
print(type(R.zone))
print(teams["TEAM.LEON"])
print(type(teams[R.zone]))
for i in range(teams[R.zone][0]):
    cycle.insert(cycle.pop(len(cycle - 1)))

for i in cycle:
	bucketList.extend(["snap(nodes[i][0], nodes[i][1])", "scan()", "scan()"])


def tick():
    time.sleep(frame/1000)

reset = "off"

tasks = {
    "wheels" : ["panic()", 10**100, "wheels"],
    "servos" : ["panic()", 10**100, "servos"],
}

def queue(task, sleep, tag, overwrite = False):
    if overwrite or tasks[tag][1] == 10**100:
        tasks[tag] = [task, time.time() - zero + sleep, tag]
    return time.time() - zero + sleep

def clear(tag):
    tasks[tag] = ["print(yourmom)", 10**100, tag]

def snap(x, y):
    x -= xy[0]
    y -= xy[1]
    dist = math.sqrt(x**2 + y**2)
    angle = math.degrees(math.asin(y/dist))
    return [polar(dist, angle), "there($x,$y)"]

def there(x, y):
    trianglulate()
    return [x, y] == xy    

def polar(distance = 0, angle = 0, marker = 0):
    global xy, innerAngle

    if marker != 0:
        distance = marker.dist
        angle = marker.bearing.y

    turn(angle)
    return queue("move({})".format(distance), abs(angle/defAngle), "wheels", True) + abs(distance/defDistance)

def move(dist):
    global xy

    xy[0] += math.cos(innerAngle * dist)
    xy[1] += math.sin(innerAngle * dist)
    if enable:
        R.motors[0] = -power
        R.motors[1] = -power
    return queue("{}()".format(reset), abs(dist/defDistance), "wheels")

def turn(angle):
    global innerAngle

    sign = angle/abs(angle)
    if enable:
        R.motors[0] = power * sign
        R.motors[1] = -power * sign
    innerAngle += angle
    return queue("{}()".format(reset), abs(angle/defAngle), "wheels")

def off():
    R.motors[0] = 0
    R.motors[1] = 0
    R.servos[0] = 0

def dropoff():
    R.servos[0] = 100
    queue("off()", 1, "servos")
    
    
def trianglulate():
    global xy, innerAngle
    clear("wheels")
    while len(list(filter(lambda x : x.info.id not in range (100, 123), R.see()))) <= 2:
        turn(defTurnAngle)
        tick()
    wall = R.see().sort(key = lambda z : z.bearing.y)
    bigger = [wall[0].bearing.y, wall[0].dist]
    smaller = [wall[1].bearing.y, wall[1].dist]
    pos_bigger = landmarks[wall[0].info.id - 100]
    pos_smaller = landmarks[wall[1].info.id - 100]
    #the distance between point a and b
    distance = math.sqrt((pos_bigger[0] - pos_smaller[0])**2 + (pos_bigger[1] - pos_smaller[1])**2)
    angle = math.asin(math.sin(bigger[0] - smaller[0])/ distance * smaller[1])
    dist = wall[0].dist
    xy = [math.cos(angle) * dist - pos_bigger[0], math.sin(angle) * dist - pos_bigger[1]]
    innerAngle = 180 - bigger[0] - angle

def scan():
    off()

    #R.see()
    tags = R.see()
    sheep = list(filter(lambda tag : tag.info.id in teams[R.zone][1], tags))

    if not sheep:
        return [turn(defTurnAngle), "scan()"]
    
    print("I see a sheep")
    return [polar(marker = sheep[0]), True]


def check():
    while True:
        todo = []
        
        for task in [*tasks.values()]: 
            if task[1] < time.time() - zero + frame/1000: 
                todo.append(task)

        todo.sort(key = lambda task : task[1])
        for task in todo:
            if task[1] > time.time() + zero:
                time.sleep(task[1] - time.time() + zero)
            eval(task[0])
            tasks[task[2]][1] = 10*100
        
        tick()
        
threading.Thread(target = check).start()   
    
while True:
    returned = eval(bucketList[0])
    timer = returned[0]
    print(timer)
    while(time.time() - zero < timer):
        tick()
        
        #if collision detection 
        #trianglulate()
        #returned = eval(bucketList[0])
        #timer = returned[0]
    if eval(returned[1]):
        bucketList.pop(0)
    

