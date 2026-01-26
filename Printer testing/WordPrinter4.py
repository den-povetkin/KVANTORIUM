from turtle import *
penup()
goto(-400,0)
factor = 2
color('black')
pensize(15 * factor)
speed(100)
printing = 0
def pixel():
    penup()
    pendown()
    forward(0)
    penup()
def forw():
    forward(10 * factor)
def back():
    left(180)
    forw()
    left(180)
def printT():
    forw()
    forw()
    left(90)
    for i in range(7):
        pixel()
        forw()
    left(90)
    forw()
    forw()
    left(180)
    for i in range(5):
        pixel()
        forw()
    forw()
    right(90)
    for i in range(7):
        forw()
    
    left(90)
def printY():
    left(90)
    forw()
    pixel()
    left(180)
    forw()
    left(90)
    for i in range(3):
        forw()
        pixel()
    forw()
    left(90)
    for i in range(6):
        forw()
        pixel()
    left(90)
    for i in range(4):
        forw()
    left(90)
    for i in range(3):
        pixel()
        forw()
    left(90)
    for i in range(3):
        forw()
        pixel()
    for i in range(4):
        forw()
    right(90)
    for i in range(3):
        forw()
    left(90)
def printF():
    forw()
    forw()
    left(90)
    for i in range(7):
        pixel()
        forw()
    def circ():
        pixel()
        forw()
        left(90)
        forw()
        pixel()
        forw()
        pixel()
        forw()
        left(90)
        forw()
        pixel()
    left(180)
    forw()
    forw()
    right(90)
    forw()
    circ()
    forw()
    forw()
    circ()
    left(180)
    for i in range(4):
        forw()
    right(90)
    for i in range(5):
        forw()
    left(90)
def printh():
    pixel()
    left(90)
    forw()
    right(90)
    for i in range(5):
        pixel()
        left(90)
        forw()
        right(90)
        forw()
    left(90)
    pixel()
    forw()
    pixel()
    left(90)
    for i in range(5):
        forw()
    left(90)
    for i in range(2):
        pixel()
        forw()
    left(90)
    forw()
    for i in range(5):
        pixel()
        right(90)
        forw()
        left(90)
        forw()
    left(180)
    forw()
    pixel()
    left(180)
    for i in range(3):
        forw()

def printCc():
    left(90)
    