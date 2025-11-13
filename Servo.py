from gpiozero import AngularServo
from time import sleep

motorL = AngularServo(24)
#motorL = AngularServo(24, min_angle=-90, max_angle=90)
#motorR = AngularServo(26, min_angle=-90, max_angle=90)
def forvard():
    motorL.angle = 90
    #motorR.angle(-90)
    
def back():
    motorL.angle= - 90
    #motorR.angle(90)
    
def left():
    motorL.angle = 90 
    motorR.angle = 90
    
def right():
    motorL.angle = -90 
    motorR.angle = -90
    
def stop():
    motorL.detach()
    #motorR.detach()

motorL.detach()
   
       
    
forvard()
sleep(5)
stop()
sleep(2)
back()
sleep(5)
stop()