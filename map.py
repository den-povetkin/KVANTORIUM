from time import sleep
ir = 1
rt = ['верх','право','низ','лево']
rotate = rt[ir]
want_rotate = ''
start_x = 0
start_y = 0
end_x = 0
end_y = 0
point_start = 0
point_end = 1
def Goto(points):
    global ir
    global want_rotate
    global start_y
    global start_x
    global rotate
    global rt
    global end_x
    global end_y
    global point_start
    global point_end
    map_i= [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5]
        ]
    # 0 - вверх 1 - вправо 2 - вниз 3 - влево

    # движение
    def move():
        print("вперёд")
        global start_y
        global start_x
        if rotate == 'верх':
            start_y -= 1
        elif rotate == 'низ':
            start_y += 1
        elif rotate == 'право':
            start_x += 1
        elif rotate == 'лево':
            start_x -= 1
        print(start_x)
        return start_x
        
    # повороты
    #def move_l():
    #    global ir
    #    global rotate
    #    print("влево")
    #    ir -= 1
    #    if ir < 0 :
    #        ir = 3
    #    rotate = rt[ir]
    def move_r():
        global ir
        global rotate
        print("вправо")
        ir += 1
        if ir > 3 :
            ir = 0
        rotate = rt[ir]
        return rotate   
        

    # основной цикл
    for i in range(len(points)-1):

        start_y = int(points[point_start][0])
        start_x = int(points[point_start][2])
        
        end_y = int(points[point_end][0])
        end_x = int(points[point_end][2])
        
        while start_y != end_y:
            if start_y > end_y:
                want_rotate = 'верх'
            if start_y < end_y:
                want_rotate = 'низ'
            while rotate != want_rotate:
                move_r()   
            move()
        while start_x != end_x:
            if start_x < end_x:
                want_rotate = 'право'
            if start_x > end_x:
                want_rotate = 'лево'
            while rotate != want_rotate:
                move_r() 
            move()
        point_start += 1
        point_end += 1
point = ['0.1','0.2','0,3','0,4','1.4','2,4','3,4','4,4','4,5','4,6','4,7']
full_path = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)]
Goto(full_path)