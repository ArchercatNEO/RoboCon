"""
Refining Zack's code to see if there are any ideas we could reuse
"""
import time
import threading
import math
from typing import NoReturn
from robotsrc import robot
from robotsrc.robot.vision import Marker

###
###   CHECK THE AREA GOTO CODE IS WORKING BY SETTING COLLECTED TO 3 OR ABOVE
###

R = robot.Robot()
R.gpio[0].mode = robot.INPUT
R.camera.res = (640, 480)

# const
PR = 80
PL = 80*0.865
THRESH = 10
collected = 0
ANGULAR_SPEED = 10
LINEAR_SPEED = 100
BEARING = 0

def front_prox_timeout():
    while True:
        time.sleep(5)
        global front_prox
        global seen_front_prox
        front_prox = False
        seen_front_prox = False

front_prox = False
seen_front_prox = False

def front_prox_loop():
    global front_prox, seen_front_prox
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

def check_front_prx():
    global front_prox
    global seen_front_prox
    #if not seen_front_prox:
    #    seen_front_prox = True
    return front_prox



#while True:
    print(check_front_prx())
    time.sleep(0.7)

def turn(degrees: float):
    """
    Turns x degrees at max speed.
    Takes additional arguments to go slower.
    """
    global BEARING

    BEARING += degrees * math.pi/180

    sign = degrees/abs(degrees)

    R.motors[0] = R.get_power(speed) * sign
    R.motors[1] = R.get_power(speed) * -sign

    await asyncio.sleep(degrees / speed)

    R.motors[0] = 0
    R.motors[1] = 0


def turn_left(sleep: float):
    R.motors[0] = PR
    R.motors[1] = -PL
    time.sleep(sleep)
    R.motors[0] = 0
    R.motors[1] = 0

def turn_right(sleep: float):
    R.motors[0] = -PR
    R.motors[1] = PL
    time.sleep(sleep)
    R.motors[0] = 0
    R.motors[1] = 0

def search_step(clockwise: bool):
    sign = -1 if clockwise  else 1
    R.motors[0] = PR * sign
    R.motors[1] = -PL * sign
    time.sleep(0.2)
    R.motors[0] = 0
    R.motors[1] = 0
    time.sleep(0.7)

def gotocube(mkrid: int):
    turnint = 0
    while check_front_prx():
        markers: list[Marker] = R.see()

        if len(markers) < 0:
            if turnint > 6:
                return False

            search_step(turnint % 2 != 0)
            turnint+=1
            continue

        for i, marker in enumerate(markers):
            if marker.info.id == mkrid:
                idx = i

        if len(markers) > 0:
            marker = markers[idx]
            distance = marker.dist
            direction = marker.bearing.y
            THRESH = 10
            if marker.dist > 1:
                THRESH = 100/marker.dist
            
            if direction > THRESH:
                turn_left(direction)
            elif direction < -THRESH:
                turn_right(direction)
            else:
                R.motors[0] = -PR
                R.motors[1] = -PL
            
    print(R.gpio[0].digital)
    return True

def collect_sequence():
    """Collect a Cube"""

    R.motors[0] = 0
    R.motors[1] = 0
    #arm servos
    print("[LOG] collecting sheep")
    time.sleep(2000)
    #if sensor in hopper crossed then return true else return false
    return False

def go_to_pen():
    """Go To Pen"""

    primarymarkerid = ""
    inpen = False
    atedge = False
    while not inpen:

        if atedge:
            #rotate 180 and move foward until tape crossed
            #dump
            continue

        if check_front_prx():
            print("reached edge")
            atedge = True
            continue

        markers: list[Marker] = R.see()
        for marker in markers:
            print(marker.info.type)

            #only if part of arena (not if home zone)
            if marker.info.type != robot.MARKER_OWNER.ARENA:
                continue

            if not marker.info.owner:
                search_step()
                continue

            if primarymarkerid == "" or not primarymarkerid in markers:
                primarymarkerid = markers[0].info.id
                print(markers[0].info.id)

            #point towards marker with primarymarkerid and move motors

def main() -> NoReturn:
    """
    main
    """
    global collected
    while True:

        markers = R.see()

        if collected > 3:
            print("[LOG] going to pen to empty")
            go_to_pen()
            continue

        if len(markers) < 0:
            search_step()
            continue

        for marker in markers:

            if marker.info.type != robot.MARKER_TYPE.SHEEP:
                print("Not a sheep")
                continue

            if not marker.info.owner:
                print("[LOG] found a sheep but we dont own it")
                continue

            print("[LOG] found a sheep and we own it")

            if gotocube(marker.info.id):

                if collect_sequence():
                    collected += 1

                else:
                    print("[LOG] lost sheep")
