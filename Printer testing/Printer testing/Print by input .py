from turtle import *
factor = 1

color('black')
pensize(1)
speed(100000)
printing = 0
def pixel():
    penup()
    pendown()
    begin_fill()
    for i in range(4):
        forward(10 * factor)
        penup()
        pendown()
        left(90)
    penup()
    end_fill()
factor = 1
def printA():
    printing = 1
    for i in range(5):
        pixel()
        left(90)
        forward(10 * factor)
        right(90)
    penup()
    forward(10 * factor)
    pendown()
    pixel()
    penup()
    forward(10 * factor)
    left(90)
    forward(10 * factor)
    right(90)
    pendown()
    for i in range(3):
        pixel()
        forward(10 * factor)
    penup()
    right(180)
    forward(10 * factor)
    left(90)
    pendown()
    for i in range(6):
        pixel()
        forward(10 * factor)
    penup()
    right(180)
    forward(10 * factor)
    forward(10 * factor)
    left(90)
    for i in range(3):
        forward(10 * factor)
    left(180)
    for i in range(3):
        pixel()
        forward(10 * factor)
    penup()
    right(90)
    forward(10 * factor)
    forward(10 * factor)
    left(90)
    forward(10 * factor)
    forward(10 * factor)
    printing = 0

word = input('Слово')
print(len(word))
for i in range(len(word)):
    if word[i] == 'а':
        printA()
    else:
        print("Такой буквы нет!")
exitonclick()