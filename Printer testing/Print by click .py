from turtle import *
import time
import pygame
pygame.init()
clock = pygame.time.Clock()
mw = pygame.display.set_mode((500,500))
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
while 1:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and printing == 0 :
            if event.key == pygame.K_a:
                printA()
    pygame.display.update() 
    clock.tick(1)
    exitonclick()

