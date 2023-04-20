import time, math, itertools
from robot import robot

class Terminator(robot.Robot):
    
    speed = 0
    
    def __init__(self, maxSpeed: float, length = 6):
        
        self.speed = maxSpeed
        
        #set initial coords to 0.25m either side away from corner and pointing to the center
        match self.zone:

            case robot.TEAM.LEON:
                self.x = 0.25
                self.y = length - 0.25
                self.angle = -45.0
            
            case robot.TEAM.ZHORA:
                self.x = length - 0.25
                self.y = length - 0.25
                self.angle = -90.0
            
            case robot.TEAM.ROY:
                self.x = length - 0.25
                self.y = 0.25
                self.angle = 90.0
            
            case robot.TEAM.PRIS:
                self.x = 0.25
                self.y = 0.25
                self.angle = 45.0

        #set up the coords of the wall markers to be used in triangulate
        self.locations = []
        for i in range(length):
            self.locations.append([i + 0.5, length])
        for i in range(length):
            self.locations.append([length, 6.5 - i])
        for i in range(length):
            self.locations.append([6.5 - i, 0])
        for i in range(length):
            self.locations.append([0, i + 0.5])

    def move(self, meters: float, speed = speed):
        
        self.x += math.cos(self.angle * math.pi/180) * meters
        self.y += math.sin(self.angle * math.pi/180) * meters

        self.motors[0] = self.getPower(speed)
        self.motors[1] = self.getPower(speed)

        time.sleep(meters / speed)

        self.motors[0] = 0
        self.motors[1] = 0

    def turn(self, degrees: float, speed = speed):

        self.angle += degrees * math.pi/180

        sign = degrees/abs(degrees)

        self.motors[0] = self.getPower(speed) * sign
        self.motors[1] = self.getPower(speed) * -sign 

        time.sleep(degrees / speed)

        self.motors[0] = 0
        self.motors[1] = 0

    def goto(self, marker):

        self.turn(marker.bearing.y)
        self.move(marker.dist)

    def snap(self, x: float, y: float):

        x -= self.x
        y -= self.y

        dist = math.sqrt(x**2 + y**2)
        angle = math.asin(y/dist)

        self.turn(angle)
        self.move(dist)

    def getPower(self, speed: float):
        return 100
    
    #use wall markers and their positions to calculate our position and angle
    def triangulate(self, markers):

        Ax = 0
        Ay = 0
        Aangle = 0
        count = 0

        #do the loop for every combination of 2 markers we have, no duplicates
        for i in itertools.permutations(markers, 2):

            count += 1
            
            m1 = i[0]
            m2 = i[1]

            x1 = self.locations[m1.info.id -100].x
            x2 = self.locations[m2.info.id -100].x
            y1 = self.locations[m1.info.id -100].y
            y2 = self.locations[m2.info.id -100].y

            d1 = m1.dist
            d2 = m2.dist

            a1 = m1.bearing.y
            a2 = m2.bearing.y

            #distance between markers (pythagoras)
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

            #trig to find an angle (law of sines)
            angle = math.asin(math.sin((a1 - a2) * math.pi/180) /distance * d2)

            Ax += math.cos(angle) * d1 - x1
            Ay += math.sin(angle) * d1 - y1
            Aangle += a1 + angle

        self.x = Ax /count
        self.y = Ay /count
        self.angle = Aangle /count

    #Look for markers, feed wall markers to triangulate and return non-wall markers
    def peek(self):

        markers = self.see()

        self.triangulate(filter(lambda marker: (marker.info.owner == robot.MARKER_OWNER.ARENA), markers))

        return filter(lambda marker: (marker.info.owner != robot.MARKER_OWNER.ARENA), markers)
    
