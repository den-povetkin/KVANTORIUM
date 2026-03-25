import pygame 
from time import sleep
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("Подключите геймпад")
    exit()
    

joystick =pygame.joystick.Joystick(0)
joystick.init()

print("Подключён ",joystick.get_name())

while True:
    pygame.event.pump()

    x = joystick.get_axis(0)
    y = joystick.get_axis(1)

    x1 = joystick.get_axis(2)
    y1 = joystick.get_axis(3)
    button_a = joystick.get_button(0)

    #print(f"X: {x:.2f}, Y: {y:.2f}, A: {button_a}")

    if x1  < -0.8:
        print('left')
        #robot.left()
    if x1  > 0.8:
        print('right')   
        #robot.right()

    if y < -0.8:
        print('forward')
        #robot.forward()
    if y > 0.8:
        print('backward')
        #robot.backward()

