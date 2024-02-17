import robot, time

R = robot.Robot()

R.gpio[1].mode = robot.OUTPUT  # Initialising the proximity sensor
R.gpio[1].digital = True  
# At 100% power for 1 second the robot moves 90cm*

refresh = 0.5

#Distances and angles travelled in 1 second with full power (angle uses 1 motor)
defDistance = 0.3
defAngle = 90

def prep():
    print("meme")

def go(distance, angle):
     turn(angle)
     wheels(100, 100, distance/defDistance)

def turn(angle):
    if angle < 0:
        wheels(100, 0, angle/abs(defAngle)) 
    else:
        wheels(0, 100, angle/abs(defAngle))

def find(cube):
    go(cube.dist, cube.bearing.y)

def wheels(left, right, turnTime):
    print(turnTime)
    R.motors[0] = -left
    R.motors[1] = -right
    time.sleep(turnTime)
    R.motors[1] = 0
    R.motors[0] = 0
    time.sleep(refresh)

while True:
    sheep = R.see()
    time.sleep(refresh)

    if sheep == []:
        turn(60)
    else :
        print("I see a sheep")
        find(sheep[0])
        time.sleep(refresh)


