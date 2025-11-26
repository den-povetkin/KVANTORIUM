from turtle import * 
ask_1=input("Ввод")
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
            
            
            
            
exitonclick()
hideturtle()