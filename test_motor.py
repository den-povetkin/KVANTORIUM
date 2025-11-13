from time import sleep
from pico import Robot
from gpiozero import Motor


api_key=api_key.api['api_key']
bot=telebot.TeleBot(api_key)

robot = Robot(left=Motor(23, 24), right=Motor(27, 22))


robot.forward()
sleep(10)
#robot.backward()
#robot.left()
#robot.right()
robot.stop()