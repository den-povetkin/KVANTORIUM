from turtle import *#появилась идея сделать отрисовку по кординатам можно сделать черз goto(ask_5,ask_6)
#также можно сделать список для удобства отрисовки фигур и добовленния новых

#функция для отрисовки линиями 
ask_1=input("Выберите Отрисовка Фигур или Отрисовка Линиями:(Комманды:Фигура,Линия)")
if ask_1=="Линия":#есть небольшая проблема с повроротами надо доработать чтобы могло быть с любыми градусами
    ask_line=input("Выберите путь вперед,налево(45,90,180,360),направо(45,90,180,360)(нет выключить):")
    while ask_line!="нет":
        if ask_line=="налево":
            ask_line_step=int(input("Значение"))
            left(ask_line_step)
        if ask_line=="направо":
            ask_line_step=int(input("Значение"))
            right(ask_line_step)
        if ask_line=="вперед":
            ask_line_step=int(input("Значение"))
            forward(ask_line_step)
        ask_line=input("Выберите путь вперед,налево,направо(нет выключить):")
#функция отрисовки фигур можно как-то доработать + добавит чтобы если нету фигуры сразу писалось "такой фигуры нет в списке"
if ask_1=="Фигура":
    ask_4=input("Выберите из перечисленых:(начиная с заглавной буквы:,Звезда,Квадрат,Круги,Квадраты)")
    ask_2=int(input("Размер:"))
    ask_3=input("Цвет:На английском:")

    def zvezda():
        for i in range(5):
            pensize(ask_2)
            color(ask_3)
            forward(50)
            left(144)
    
    def squre():
        for i in range(5):
            pensize(ask_2)
            color(ask_3)
            forward(90)
            left(90)

    def squre_figure():
        for i in range(5):
            pensize(ask_2)
            color(ask_3)
            forward(90)
            left(90)
            forward(90)
            left(45)
            forward(90)
            left(45)
            forward(90)
            left(45)
            forward(90)

    def circle_fugure():
        for i in range(7):
            circle(radius=ask_2)
            color(ask_3)
            left(50)

    if ask_4=="Звезда":
        zvezda()

    if ask_4=="Квадрат":
        squre()

    if ask_4=="Круги":
        circle_fugure()

    if ask_4=="Квадраты":
        squre_figure()

    else:
        print("такой фигуры нет в списке") 
    

exitonclick()
