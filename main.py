from turtle import *
from time import sleep
from pico import Robot
from gpiozero import Motor


t1 = Turtle()
t1.color('orange')
t1.pensize(10)
t1.speed(1)

#robot = Robot(left=Motor(23, 24), right=Motor(27, 22))

def bukvaP():
    t1.left(90)
    t1.forward(100)
    t1.right(90)
    t1.forward(50)
    t1.right(90)
    t1.forward(100)
    t1.penup()
    t1.left(90)
    t1.forward(30)
    t1.pendown()
    
def bukvaR():
    t1.left(90)
    t1.forward(100)
    t1.right(90)
    t1.forward(50)
    t1.right(90)
    t1.forward(50)
    t1.right(90)
    t1.forward(50)
    t1.penup()
    t1.left(90)
    t1.forward(50)
    t1.left(90)
    t1.forward(50)
    t1.forward(10)
    t1.pendown()

abc = input ('Введите слово: ')

for bu in abc: 
    if bu == 'п':
        bukvaP()
    elif bu == 'р':
        bukvaR()
    else:
        print ('такую букву я не знаю')
#sleep(10)