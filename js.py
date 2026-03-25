import telebot
from telebot import types
import api_key
from pico import Robot
from gpiozero import Motor
from time import sleep
from RobotPathFinder import RobotPathFinder
import pygame 
from time import sleep
    #print(f"X: {x:.2f}, Y: {y:.2f}, A: {button_a}")    
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time
global full_path , optimized_path, current_path, uid

robot = Robot(left=Motor(23, 24), right=Motor(27, 22))

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

    x = joystick.get_axis(2)
    y = joystick.get_axis(1)

    button_a = joystick.get_button(0)

    #print(f"X: {x:.2f}, Y: {y:.2f}, A: {button_a}")

    if x  < -0.8:
        robot.left()
    elif x  > 0.8:  
        robot.right()
    elif y < -0.8:
        robot.forward()
    elif y > 0.8:
        robot.backward()
    else:
        robot.stop()