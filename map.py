from time import sleep
def Goto(points):
    global ir
    global im
    global il
    global want_rotate
    global start_y
    global start_x
    global rotate_i
    global best_rotate
    global x1
    global x2
    map_i= [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5]
        ]
    # 0 - вверх 1 - вправо 2 - вниз 3 - влево
    ir = 1
    rt = ['верх','право','низ','лево']
    rotate = rt[ir]
    want_rotate = ''
    im = ir
    il = ir
    rotate_i = rotate
    best_rotate = ''
    x1 = 0
    x2 = 0
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
    # повороты
    def move_l():
        global ir
        global rotate
        print("влево")
        ir -= 1
        if ir < 0 :
            ir = 3
        rotate = rt[ir]
    def move_r():
        global ir
        global rotate
        print("вправо")
        ir += 1
        if ir > 3 :
            ir = 0
        rotate = rt[ir]
    def left():
        global il
        global rotate_i
        il -= 1
        if il < 0 :
            il = 3
        rotate_i = rt[il]
    def right():
        global im
        global rotate_i
        im += 1
        if im > 3 :
            im = 0
        rotate_i = rt[im]
        
    def move_rotate():
        global best_rotate
        global want_rotate
        global ir
        global il
        global im
        global rotate_i
        global x1
        global x2
        x1 = 0
        x2 = 0
        rotate_i = rotate
        il = ir
        while rotate_i != want_rotate:
            left()
            x1 += 1
        rotate_i = rotate
        im = ir
        while rotate_i != want_rotate:
            right()
            x2 += 1
        rotate_i = rotate
        best_rotate = min(x1,x2)
        if x1 < x2:
            for i in range(best_rotate):
                move_l()
        else:
            for i in range(best_rotate):
                move_r()
            
    point_start = 0
    point_end = 1
    # основной цикл
    for i in range(len(points)-1):

        start_y = int(points[point_start][0])
        start_x = int(points[point_start][2])
        
        end_y = int(points[point_end][0])
        end_x = int(points[point_end][2])
        
        while start_y != end_y:
            if start_y > end_y:
                want_rotate = 'низ'
            if start_y < end_y:
                want_rotate = 'верх'
            if rotate != want_rotate:
                move_rotate()
            move()
        while start_x != end_x:
            if start_x < end_x:
                want_rotate = 'право'
            if start_x > end_x:
                want_rotate = 'лево'
            if rotate != want_rotate:
                move_rotate()
            move()
        point_start += 1
        point_end += 1
point = ['1.1','1.2','1,3','1,4','2,4','3,4','4,4','4,5','4,6','4,7']
full_path = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)]
Goto(point)