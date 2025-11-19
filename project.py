import turtle

def kv():
    """Рисует квадрат с использованием turtle"""
    t = turtle.Turtle()
    
    # Рисуем квадрат
    for i in range(4):
        t.forward(100)  # Длина стороны квадрата
        t.right(90)     # Поворот на 90 градусов
    
    # Закрываем экран по клику
    turtle.exitonclick()

def circle():
    """Рисует круг с использованием turtle"""
    t = turtle.Turtle() 
    # Рисуем круг
    t.circle(50)  # Радиус круга
    
    # Закрываем экран по клику
    turtle.exitonclick()

def triangle():
    """Рисует треугольник с использованием turtle"""
    t = turtle.Turtle()
    
    # Рисуем треугольник
    for i in range(3):
        t.forward(100)  # Длина стороны треугольника
        t.right(120)    # Поворот на 120 градусов

    # Закрываем экран по клику
    turtle.exitonclick()

def circle36():
    """Рисует супер круг с использованием turtle"""
    t = turtle.Turtle() 
    # Рисуем круг
    for i in range(36):
        t.circle(50)  # Радиус круга
        t.right(10)
    
    # Закрываем экран по клику
    turtle.exitonclick()

# kv()
# circle()
#triangle()
circle36()
