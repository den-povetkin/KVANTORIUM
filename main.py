from turtle import *
from time import sleep

# переменные
t1 = Turtle()
t1.color('orange')
t1.pensize(20)
t1.speed(1)
t1.shape('square')

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
    t1.penup()
    t1.forward(20)
    t1.pendown()
def probel():
    t1.penup()
    t1.forward(30)
    t1.pendown()

abc = input ('Введите слово: ')

for bu in abc: 
    if bu == 'п':
        bukvaP()
    elif bu == 'р':
        bukvaR()
    elif bu == ' ':
        probel()    
    else:
        probel()
#sleep(10)

# ля ля ля проверка