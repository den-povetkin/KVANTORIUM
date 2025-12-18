from gpiozero import AngularServo
from time import sleep

motorL = AngularServo(24)
#motorL = AngularServo(24, min_angle=-90, max_angle=90)
#motorR = AngularServo(26, min_angle=-90, max_angle=90)
def forvard():
    """
    Функция для движения вперед.
    Устанавливает угол сервопривода motorL на 90 градусов.
    """
    motorL.angle = 90
    #motorR.angle(-90)
    
def back():
    """
    Функция для движения назад.
    Устанавливает угол сервопривода motorL на -90 градусов.
    """
    motorL.angle= - 90
    #motorR.angle(90)
    
def left():
    """
    Функция для поворота влево.
    Устанавливает угол сервоприводов motorL и motorR на 90 градусов.
    """
    motorL.angle = 90
    motorR.angle = 90
    
def right():
    """
    Функция для поворота вправо.
    Устанавливает угол сервоприводов motorL и motorR на -90 градусов.
    """
    motorL.angle = -90
    motorR.angle = -90
    
def stop():
    """
    Функция для остановки.
    Отключает сервопривод motorL.
    """
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