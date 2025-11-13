from WordPrinter import *
while True: 
    i1 = 0
    word = input('Слово: ')
    print(len(word))
    for i in range(len(word)):
        if word[i1] == 'а':
            printA()
        if word[i1] == 'б':
            printb()
        if word[i1] == 'в':
            printB()
        if word[i1] == 'г':
            printGe()
        if word[i1] == 'д':
            printD()
        if word[i1] == 'е':
            printE()   
        if word[i1] == 'ё':
            printio()
        i1 = i1 + 1
   
exitonclick()