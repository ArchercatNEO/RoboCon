#Positive = anticlockwise
#Negative = clockwise

from robot.wrapper import Robot


def lift(robot: Robot):
    robot.servos[0] = 100

def drop(robot: Robot):
    robot.servos[0] = -100

def open_arms(robot: Robot):
    robot.servos[1] = 300
    robot.servos[2] = 200

def close(robot: Robot):
    robot.servos[1] = 100
    robot.servos[2] = 200