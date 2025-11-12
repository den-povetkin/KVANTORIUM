from turtle import *
t1 = Turtle()
t1.color('orange')
t1.pensize(10)
'''''
left_motor = Motor(forward=17, backward=18)
right_motor = Motor(forward=22, backward=23)


class Robot:
    def __init__(self, left_motor = None, right_motor = None  ):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def move_forward(speed=1.0):
    left_motor.forward(speed)
    right_motor.forward(speed)

    def move_backward(speed=1.0):
    left_motor.backward(speed)
    right_motor.backward(speed)
    def move_left(speed=1.0):
    left_motor.backward(speed)
    right_motor.forward(speed)
    def move_right(speed=1.0):
    left_motor.forward(speed)
    right_motor.backward(speed)
    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()

'''
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
