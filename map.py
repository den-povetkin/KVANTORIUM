map_i= [
    [0, 1, 2, 3],
    [0, 1, 2, 3],
    [0, 1, 2, 3],
    [0, 1, 2, 3]]
start_y = 3
start_x = 2
end_y = 0
end_x = 3
ir = 1
rt = ['верх','право','низ','лево']
rotate = rt[ir]
want_rotate = ''
im = ir
rotate_i = rotate
best_rotate = ''
x1 = 0
x2 = 0
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
def move_l():

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
    global im
    global rotate_i
    im += 1
    print("робот2:",im)
    if im > 3 :
        im = 0
    rotate_i = rt[im]
def right():
    global im
    global rotate_i
    im -= 1
    print("робот:",im)
    if im < 0 :
        im = 3
    rotate_i = rt[im]

def move_rotate():
    global best_rotate
    global want_rotate
    global ir
    global rotate_i
    global x1
    global x2
    x1 = 0
    x2 = 0
    rotate_i = rotate
    while rotate_i != want_rotate:
        left()
        x1 += 1
    rotate_i = rotate
    im = ir
    while rotate_i != want_rotate:
        right()
        x2 += 1
    rotate_i = rotate
    im = ir
    print(x1)
    print(x2)
    if x1 > x2:
        move_l()
    else:
        move_r()
        
while start_y != end_y:
    if start_y > end_y:
        want_rotate = 'верх'
    if start_y < end_y:
        want_rotate = 'низ'
    while rotate != want_rotate:
        move_rotate()
    move()




    