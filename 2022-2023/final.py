# TODO:
#Collision detection in main loop how???????
#Finish dropoff()
#rewrite planning

import robot, threading, time, math

def tick():
    time.sleep(frame/1000)

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
    angle = math.asin(y/dist) * 180/math.pi
    return [polar(dist, angle), f"there({x}, {y})"]

def there(x, y):
    trianglulate()
    return [x, y] == xy    

def polar(distance = 0, angle = 0, marker = 0):
    global xy, innerAngle

    if marker != 0:
        distance = marker.dist + 0.1
        angle = marker.bearing.y

    turn(angle)
    return queue(f"move({distance})", abs(angle/defAngle), "wheels", True) + abs(distance/defDistance)

def move(dist):
    global xy
    print(f"moving {dist} meters in {abs(dist/defDistance)} seconds")

    xy[0] += math.cos(innerAngle * dist * math.pi / 180)
    xy[1] += math.sin(innerAngle * dist * math.pi / 180)
    if enable:
        R.motors[0] = power * motorFactor
        R.motors[1] = power
        time.sleep(abs(dist/defDistance))
        off()
    return queue(f"{reset}()", abs(dist/defDistance), "wheels")

def turn(angle):
    global innerAngle
    print(f"turning {angle} degrees in {abs(angle/defAngle)} seconds")

    sign = angle/abs(angle)
    if enable:
        R.motors[0] = power * sign * motorFactor
        R.motors[1] = -power * sign
        time.sleep(abs(angle/defAngle))
        off()
    innerAngle += angle
    return queue(f"{reset}()", abs(angle/defAngle), "wheels")

def off():
    R.motors[0] = 0
    R.motors[1] = 0
    R.servos[0] = 0

def dropoff():
    R.servos[0] = 100
    queue("off()", 1, "servos")
    
    


#	http://www.movable-type.co.uk/scripts/latlong.html
#	https://stackoverflow.com/questions/24970605/finding-third-points-of-triangle-using-other-two-points-with-known-distances
#	https://www.igismap.com/formula-to-find-bearing-or-heading-angle-between-two-points-latitude-longitude/

def trianglulate():
    global xy, innerAngle

    #finding 2+ wall markers
    clear("wheels")
    tags = list(filter(lambda x : x.info.id in range (100, 123), R.see()))
    while len(tags) < 2:
        turn(defTurnAngle)
        tags = list(filter(lambda x : x.info.id in range (100, 123), R.see()))
        tick()
    
    #sorting by two closest markers then sorting by angle
    wall = sorted(tags, key = lambda z : z.dist)
    wall = wall[:2]
    wall = sorted(tags, key = lambda z : z.bearing.y)

    #setting up variables
    m1x = landmarks[wall[0].info.id - 100][0]
    m1y = landmarks[wall[0].info.id - 100][1]
    m1dist = wall[0].dist
    m1bearing = wall[0].bearing.y

    m2x = landmarks[wall[1].info.id - 100][0]
    m2y = landmarks[wall[1].info.id - 100][1]
    m2dist = wall[1].dist

    #the distance between point a and b
    distance = math.sqrt((m1x - m2x)**2 + (m1y - m2y)**2)

    #Cosine theorem
    cos_phi = (distance**2 + m1dist**2 - m2dist**2) / (2*distance*m1dist)
    sin_phi = math.sqrt(1 - cos_phi**2)

    #calculating the robot's xy coordinate
    xp = m1x + m1dist/distance * (cos_phi * (m2x - m1x) - sin_phi * (m2y- m1y))
    yp = m1y + m1dist/distance * (sin_phi * (m2x - m1x) + cos_phi * (m2y- m1y))

    xn = m1x + m1dist/distance * (cos_phi * (m2x - m1x) + sin_phi * (m2y- m1y))
    yn = m1y + m1dist/distance * (-sin_phi * (m2x - m1x) + cos_phi * (m2y- m1y))

    if 0 <= xp <= 6 and 0 <= yp <= 6:
        xy = [xp, yp]
    else:
        xy = [xn, yn]

    #calculate bearing relative to the x axis
    conversion = 1E-4
    long1 = conversion * xy[0]
    lat1 = conversion * xy[1]
    long2 = conversion * m1x
    lat2 = conversion * m1y

    diflat = lat2 - lat1
    diflong = long2 - long1

    atanx = math.cos(lat2) * math.sin(diflong)
    atany = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(diflong)

    bearingRad = math.atan2(atany, atanx)
    bearingDegrees = bearingRad * 180/math.pi

    innerAngle = bearingDegrees + m1bearing

#Find a sheep and eat it
def scan():
    off()

    tags = R.see()
    sheep = list(filter(lambda tag : tag.info.id in teams[R.zone][1], tags))

    if not sheep:
        return [turn(defTurnAngle), "false()"]

    sheep = sorted(sheep, key = lambda z : z.dist)
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



R = robot.Robot()

R.gpio[0].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[0].digital = True  

R.gpio[1].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[1].digital = True  

# Distances and angles travelled in 1 second with 100 power 
# At 100% power for 1 second the robot moves 180 degrees or 0.3 meters
defDistance = 0.83/5
defAngle = 270/4.5
power = 100
defTurnAngle = 15
motorFactor = 0.93

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

for i in range(teams[R.zone][0]):
    cycle.insert(cycle.pop(len(cycle) - 1))

for i in cycle:
    x = nodes[i][0]
    y = nodes[i][1]
    bucketList.extend(["snap({}, {})".format(x, y), "scan()", "scan()"])

reset = "off"

tasks = {
    "wheels" : ["panic()", 10**100, "wheels"],
    "servos" : ["panic()", 10**100, "servos"],
}
print(bucketList)

#threading.Thread(target = check).start()   
    
while True:

    scan()
    snap(2.5, 4.5)
    scan()
    scan()
    snap(4.5, 1.5)
    scan() 
    scan()
    snap(1.5, 1.5)
    scan()
    scan(), 
    snap(1.5, 4.5) 
    scan() 
    scan()


    #move(1)
    trianglulate()
    print(xy)
    print(innerAngle)
    snap((2.5 + xy[0])/2, (4.5+ xy[1])/2) 
    trianglulate()
    snap(0.5, 5.5)
    break






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




        

    
