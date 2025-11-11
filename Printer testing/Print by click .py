from turtle import *


factor = 1
t1 = Turtle()
t1.color('black')
t1.pensize(10 * factor)

def pixel():
    t1.penup()
    t1.pendown()
    t1.begin_fill()
    for i in range(4):
        t1.forward(100 * factor)
        t1.penup()
        t1.pendown()
        t1.left(90)
    t1.end_fill()
pixel()
exitonclick()