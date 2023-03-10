import robot
import time
import threading

###
###   CHECK THE AREA GOTO CODE IS WORKING BY SETTING COLLECTED TO 3 OR ABOVE
###

R = robot.Robot()
R.gpio[0].mode = robot.INPUT
R.camera.res = (640, 480)

# const
Pr = 80
Pl = 80*0.865
THRESH = 10


front_prox_timeout = 5
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

def check_front_prx():
    global front_prox
    global seen_front_prox
    #if not seen_front_prox:
    #    seen_front_prox = True
    return front_prox



while True:
    print(check_front_prx())
    time.sleep(0.7)



def turn_left(direction):
    R.motors[0] = Pr
    R.motors[1] = -Pl
    time.sleep(2/direction)
    R.motors[0] = 0
    R.motors[1] = 0

def turn_right(direction):
    R.motors[0] = -Pr
    R.motors[1] = Pl
    time.sleep(-(2/direction))
    R.motors[0] = 0
    R.motors[1] = 0

def search_step():
    R.motors[0] = Pr
    R.motors[1] = -Pl
    time.sleep(0.2)
    R.motors[0] = 0
    R.motors[1] = 0
    time.sleep(0.7)

def gotocube(mkrid):
    turnint = 0
    while check_front_prx():
        markers = R.see()

        i=0
        for m in markers:
            if m.info.id == mkrid:
                idx = i
                break
            i+=1

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
                R.motors[0] = -Pr
                R.motors[1] = -Pl
        else:
            if turnint < 6:
                if turnint%2 == 0:
                    R.motors[0] = Pr
                    R.motors[1] = -Pl
                    time.sleep(0.2)
                    R.motors[0] = 0
                    R.motors[1] = 0
                    time.sleep(0.7)
                    turnint+=1
                else:
                    R.motors[0] = -Pr
                    R.motors[1] = Pl
                    time.sleep(0.2)
                    R.motors[0] = 0
                    R.motors[1] = 0
                    time.sleep(0.7)
                    turnint+=1
            else:
                return False
    print(R.gpio[0].digital)
    return True

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



        


