from time import sleep
from pico import Robot
from gpiozero import Motor

robot = Robot(right=Motor(23, 24), left=Motor(27, 22))

#robot.forward()
#robot.backward()
#robot.left()
#robot.right()

def Step(x):
    robot.forward()
    sleep(x)
    robot.stop()
# 0.9 сек поворот на 90 градусов
def StepLeft(x):
    robot.left()
    sleep(x)
    robot.stop()
    
def StepRight(x):
    robot.right()
    sleep(x)
    robot.stop()
    
def StepBackward(x):
    robot.backward()
    sleep(x)
    robot.stop()

#StepBackward(0.9)
for i in range(36):
    Step(2)
    StepRight(0.1)
