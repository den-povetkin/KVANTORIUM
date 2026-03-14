
def edit_robot_speed():
    global speeds
    q = input('move or rotate ')
    speed = float(input('speed '))
    move_s = 0
    rotate_s = 0
    if q == 'm':
        move_s = speed
    elif q == 'r':
        rotate_s = speed    
    with open('robot_speed.txt', 'r' , encoding = 'utf-8') as file:
        speeds = []
        for line in file:
            data = line.split(' ')
            speeds.append(float(data[1]))
    with open('robot_speed.txt', 'w' , encoding = 'utf-8') as file:
        data = file
        edit = input('edit(y/n) ')
        if edit == 'y':
            if move_s == speed:
                data.writelines('speed_rotate: '+ str(speeds[0]) + '\n' + 'speed_move: '+ str(move_s) + ' ')
            if rotate_s == speed:
                data.writelines('speed_rotate: '+ str(rotate_s) + '\n' + 'speed_move: '+ str(speeds[1])+ ' ')
    with open('robot_speed.txt', 'r' , encoding = 'utf-8') as file:
        speeds = []
        for line in file:
            data = line.split(' ')
            speeds.append(float(data[1]))
    print('скороть поворота: ' + str(speeds[0]))
    print('скороть движения: ' + str(speeds[1]))
    
    return speeds
