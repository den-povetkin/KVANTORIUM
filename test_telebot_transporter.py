import telebot
from telebot import types
import api_key
from pico import Robot
from gpiozero import Motor
from time import sleep
from RobotPathFinder import RobotPathFinder

import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time
global full_path , optimized_path, current_path, uid
full_path = None

api_key=api_key.api['api_key']
bot=telebot.TeleBot(api_key)
sleep_time = 0.57
#ADMIN = 19907153
ADMIN = 0

robot = Robot(left=Motor(23, 24), right=Motor(27, 22))

# Инициализация I2C
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
speeds = []
# Настройка PN532
pn532.SAM_configuration()
with open('robot_speed.txt', 'r' , encoding = 'utf-8') as file:
    for line in file:
        data = line.split(' ')
        speeds.append(float(data[1]))
@bot.message_handler(commands=['id'])
def send_id(message: types.Message):
    # Отправка id
    bot.reply_to(message, text = str(message.chat.id))
    
@bot.message_handler(commands=['start'])
def start(message):
        if message.chat.id == ADMIN:
        #клавиатура
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard = True)
            btn1=types.KeyboardButton('кнопка')
            btn2=types.KeyboardButton('кнопка')
            btn3=types.KeyboardButton('кнопка')
            btn4=types.KeyboardButton('кнопка')
            markup.add(btn1, btn2, btn3, btn4)
        # отправление клавиатуры с текстом
            bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup) 
        else:
            markup =types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn1 = types.KeyboardButton("Задать маршрут")
            btn2 = types.KeyboardButton("Показать карту")
            btn3 = types.KeyboardButton("Калибровка")
            btn4 = types.KeyboardButton("О нас")
            btn5 = types.KeyboardButton("Ручное управление")
            markup.add(btn1, btn2, btn3, btn4, btn5 )
            bot.send_message(message.chat.id, text="Привет, {0.first_name}! Выбирай что будем делать".format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "О нас":
        long_text(message)
    
    elif message.text == "Задать маршрут":
        #bot.send_message(message.chat.id, text="Привет тут будем Задать маршрут")
        start_welcome(message)
        
    elif message.text == "Показать карту":
        bot.send_message(message.chat.id, text="Привет тут будем Показать карту")
        #search_point()
        gogo()

        
    elif message.text == "Калибровка":
        bot.send_message(message.chat.id, text="Привет тут будем калибровать шаг робота",reply_markup= create_speed_type_keyboard())
        
    elif message.text == "Ручное управление":
        bot.send_message(message.chat.id, text="Привет тут будет ручное управление")
        bot.reply_to(message, "Привет! Я робот-Пико. Используй кнопки ниже для управления.",
        reply_markup=create_robot_keyboard())


    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")
'''
def create_edit_keyboard():
    keyboard = types.InlineKeyboardMarkup()
            
    btn_r = types.InlineKeyboardButton(text="поворот", callback_data="r")
    btn_m = types.InlineKeyboardButton(text="скорость", callback_data="m")
    bot.register_next_step_handler(,calibrovca)
    keyboard.add(btn_r,btn_m)
    return keyboard
'''
@bot.message_handler(content_types=['text'])
def calibrovca(message):
    global sleep_time , calibrovca_1 , speeds
    robot.right()
    sleep(float(message.text))
    calibrovca_1 = float(message.text)
    robot.stop()
    bot.send_message(message.chat.id, text="Подтвердить изменения?(да\нет)",)
    bot.register_next_step_handler(message,edit_value)
    
def edit_value():
    global speeds
    with open('robot_speed.txt', 'w' , encoding = 'utf-8') as file:
        data = file
        data.writelines('speed_rotate: '+ str(calibrovca_1) + '\n' + 'speed_move: '+ str(speeds[1]) + ' ')
    with open('robot_speed.txt', 'r' , encoding = 'utf-8') as file:
        speeds = []
        for line in file:
            data = line.split(' ')
            speeds.append(float(data[1]))
    print('скороть поворота: ' + str(speeds[0]))
    print('скороть движения: ' + str(speeds[1]))
    bot.send_message(message.chat.id, text='Откалиброван')
                
    return speeds

        
def create_speed_type_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    
    btn_rotate = types.InlineKeyboardButton(text='поворот' , callback_data='rotating')
    btn_move = types.InlineKeyboardButton(text='движение' , callback_data='moving')
    
    keyboard.add(btn_rotate,btn_move)
    
    return keyboard
def create_confim_changes_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    
    btn_rotate = types.InlineKeyboardButton(text='да' , callback_data='cc')
    btn_move = types.InlineKeyboardButton(text='нет' , callback_data='ncc')
    
    keyboard.add(btn_rotate,btn_move)
    
    return keyboard
def long_text(message): #! отправка длинного сообщения через текстовый файл 
    if message.text == "О нас":
        with open('hi.txt', "r", encoding = "UTF-8") as file:
            data = file.read()
        bot.send_message(message.chat.id, text=data)


def create_robot_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    button_forward = types.InlineKeyboardButton(text="Вперед", callback_data="forward")
    button_backward = types.InlineKeyboardButton(text="Назад", callback_data="backward")
    button_left = types.InlineKeyboardButton(text="Налево", callback_data="left")
    button_right = types.InlineKeyboardButton(text="Направо", callback_data="right")
    button_stop = types.InlineKeyboardButton(text="Стоп", callback_data="stop")

    keyboard.add(button_forward, button_backward)
    keyboard.add(button_left, button_right)
    keyboard.add(button_stop)

    return keyboard

def create_yesno_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    button_yes = types.InlineKeyboardButton(text="Да", callback_data="yes")
    button_no = types.InlineKeyboardButton(text="Нет", callback_data="no")


    keyboard.add(button_yes, button_no)
    
    return keyboard

current_path = {
        'past': ['(0, 0)'],
        'current': ['(0, 0)'],
        'future': ['(0, 0)'],
                }
           
environment = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]

path_finder = RobotPathFinder(
    matrix=environment,
    obstacles=[1],
    allow_diagonal=False,
    robot_size=1
)

points_to_visit = []

def create_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    button_add_point = types.InlineKeyboardButton(text="Добавить точку", callback_data="add_point")
    button_find_path = types.InlineKeyboardButton(text="Найти путь", callback_data="find_path")
    button_show_points = types.InlineKeyboardButton(text="Показать точки", callback_data="show_points")
    button_reset = types.InlineKeyboardButton(text="Сброс", callback_data="reset")

    keyboard.add(button_add_point, button_find_path)
    keyboard.add(button_show_points, button_reset)
    
    return keyboard

def create_point_input_keyboard():
    """Создание клавиатуры для ввода координат точки"""
    keyboard = types.InlineKeyboardMarkup()
    
    # Создаем кнопки для строк (0-9)
    row_buttons = []
    for i in range(5):
        row_buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=f"row_{i}"))
    
    # Добавляем кнопки по 5 в ряд
    for i in range(0, 10, 5):
        keyboard.row(*row_buttons[i:i+5])
    
    # Кнопка отмены
    cancel_btn = types.InlineKeyboardButton(text="Отмена", callback_data="cancel_point")
    keyboard.add(cancel_btn)
    
    return keyboard

def create_column_keyboard(selected_row):
    """Создание клавиатуры для выбора столбца после выбора строки"""
    keyboard = types.InlineKeyboardMarkup()
    
    # Создаем кнопки для столбцов (0-9)
    col_buttons = []
    for i in range(5):
        col_buttons.append(types.InlineKeyboardButton(text=str(i), callback_data=f"point_{selected_row}_{i}"))
    
    # Добавляем кнопки по 5 в ряд
    for i in range(0, 10, 5):
        keyboard.row(*col_buttons[i:i+5])
    
    # Кнопка отмены
    cancel_btn = types.InlineKeyboardButton(text="Отмена", callback_data="cancel_point")
    keyboard.add(cancel_btn)
    
    return keyboard

def format_path_for_telegram(path):
    """Форматирование пути для отображения в Telegram"""
    if not path:
        return "Путь не найден"
    
    formatted = "Путь найден:\n"
    for i, pos in enumerate(path):
        formatted += f"{i+1}. ({pos[0]}, {pos[1]})\n"
    
    return formatted

def visualize_path_for_telegram(path, points=None):
    """Адаптация визуализации пути для Telegram"""
    # Используем существующий метод визуализации
    visualization = path_finder.visualize_path(path=path, points=points)
    return f"Визуализация пути:\n```\n{visualization}\n```"

def first_point():
    text = ''
    status = True
    global uid
    # Инициализация I2C
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)

    # Настройка PN532
    pn532.SAM_configuration()

    print("Ожидание NFC метки...")
#    print("Поднесите карту к считывателю")

    while status == True:
        # Проверка наличия карты
        uid = pn532.read_passive_target(timeout=0.5)
        
        if uid is not None:
            print("Найдена карта с UID:", [hex(i) for i in uid])
            status = False

            
            # Обработка разных типов карт
            try:
                # Для Mifare Classic
                if len(uid) == 4:
                    print("Тип: Mifare Classic")
                    print("Чтение блока данных...")
                    
                    # Аутентификация и чтение блока
                    key = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # ключ по умолчанию
                    authenticated = pn532.mifare_classic_authenticate_block(
                        uid, 4, pn532.MIFARE_CMD_AUTH_A, key)
                    
                    if authenticated:
                        data = pn532.mifare_classic_read_block(4)
                        print(f"Данные блока 4: {data.hex()}")
                        
                        # Пример записи данных
                        # new_data = b'Hello Raspberry!'
                        # if len(new_data) <= 16:
                        #     pn532.mifare_classic_write_block(4, new_data.ljust(16, b'\x00'))
                        
                # Для NTAG
                elif len(uid) == 7:
                    #print("Тип: NTAG")
                    # Чтение текста из нескольких страниц NTAG
                    text_data = b''
                    page_index = 4  # Начинаем чтение с 4-й страницы
                    
                    # Читаем несколько страниц для получения полного текста
                    for i in range(8):  # Читаем 8 страниц (32 байта)
                        try:
                            page_data = pn532.ntag2xx_read_block(page_index + i)
                            if page_data is not None:
                                # Проверяем, содержит ли страница данные окончания текста
                                if b'\x00\x00' in page_data or page_data == b'\x00' * 4:
                                    # Добавляем данные до первого нулевого байта
                                    for j, byte in enumerate(page_data):
                                        if byte == 0:
                                            text_data += page_data[:j]
                                            break
                                    else:
                                        text_data += page_data
                                    break
                                text_data += page_data
                              #  print(f"Данные страницы {page_index + i}: {page_data.hex()}")
                            else:
                                break
                        except Exception as e:
                            print(f"Ошибка чтения страницы {page_index + i}: {e}")
                            break
                    
                    # Пытаемся декодировать текст
                    try:
                        # Удаляем пустые байты в конце и декодируем
                        text = text_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
                        if text:
                            print(f"Текст с метки: {text}")
                        else:
                            print(f"Данные в виде hex: {text_data.hex()}")
                    except Exception as e:
                        print(f"Ошибка декодирования текста: {e}")
                        print(f"Данные в виде hex: {text_data.hex()}")
                    
            except Exception as e:
                print(f"Ошибка: {e}")
            
            cid=str(text)
            row=int(cid[8])
            col=int(cid[10])
            points_to_visit.append((row, col))
            print(points_to_visit)

current_path = []
            
def gogo():
    text = ''
    status = True
    # Инициализация I2C
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)

    # Настройка PN532
    pn532.SAM_configuration()

    print("Ожидание NFC метки...")
#    print("Поднесите карту к считывателю")

    while status == True:
        # Проверка наличия карты
        uid = pn532.read_passive_target(timeout=1.5)
        
        if uid is not None:
            print("Найдена карта с UID:", [hex(i) for i in uid])
            status = False

            
            # Обработка разных типов карт
            try:
                # Для Mifare Classic
                if len(uid) == 4:
                    print("Тип: Mifare Classic")
                    print("Чтение блока данных...")
                    
                    # Аутентификация и чтение блока
                    key = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # ключ по умолчанию
                    authenticated = pn532.mifare_classic_authenticate_block(
                        uid, 4, pn532.MIFARE_CMD_AUTH_A, key)
                    
                    if authenticated:
                        data = pn532.mifare_classic_read_block(4)
                        print(f"Данные блока 4: {data.hex()}")
                        
                        # Пример записи данных
                        # new_data = b'Hello Raspberry!'
                        # if len(new_data) <= 16:
                        #     pn532.mifare_classic_write_block(4, new_data.ljust(16, b'\x00'))
                        
                # Для NTAG
                elif len(uid) == 7:
                    #print("Тип: NTAG")
                    # Чтение текста из нескольких страниц NTAG
                    text_data = b''
                    page_index = 4  # Начинаем чтение с 4-й страницы
                    
                    # Читаем несколько страниц для получения полного текста
                    for i in range(8):  # Читаем 8 страниц (32 байта)
                        try:
                            page_data = pn532.ntag2xx_read_block(page_index + i)
                            if page_data is not None:
                                # Проверяем, содержит ли страница данные окончания текста
                                if b'\x00\x00' in page_data or page_data == b'\x00' * 4:
                                    # Добавляем данные до первого нулевого байта
                                    for j, byte in enumerate(page_data):
                                        if byte == 0:
                                            text_data += page_data[:j]
                                            break
                                    else:
                                        text_data += page_data
                                    break
                                text_data += page_data
                              #  print(f"Данные страницы {page_index + i}: {page_data.hex()}")
                            else:
                                break
                        except Exception as e:
                            print(f"Ошибка чтения страницы {page_index + i}: {e}")
                            break
                    
                    # Пытаемся декодировать текст
                    try:
                        # Удаляем пустые байты в конце и декодируем
                        text = text_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
                        if text:
                            print(f"Текст с метки: {text}")
                        else:
                            print(f"Данные в виде hex: {text_data.hex()}")
                    except Exception as e:
                        print(f"Ошибка декодирования текста: {e}")
                        print(f"Данные в виде hex: {text_data.hex()}")
                    
            except Exception as e:
                print(f"Ошибка: {e}")
            
            cid=str(text)
            row=int(cid[8])
            col=int(cid[10])
            new_element=(row,col) 
            if new_element not in current_path:
                current_path.append(new_element)

            #current_path.append((row, col))
            print(current_path)
            #status = True

        
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

def move():
    print('вперёд')
    robot.forward()
    sleep(1)
    gogo()
    all_in = False
           
    print(f'OP: {optimized_path}')
    print(f'CP: {current_path}')

    all_in = any(item in optimized_path for item in current_path)
    print(all_in)  # Вывод: True
    if all_in == True:
        robot.stop()
    else:
        robot.forward()
#        robot.stop()
'''    if rotate == 'верх':
        start_y -= 1
    elif rotate == 'низ':
        start_y += 1
    elif rotate == 'право':
        start_x += 1
    elif rotate == 'лево':
        start_x -= 1
    return start_x, start_y
'''
def rotate_robot():
    global rotate,ir
    print('right')
    robot.right()
    ir += 1
    if ir > 3:
        ir = 0
    rotate = rt[ir]
'''
    def create_best_rotate(want_rotate,rotate,ir):
        n_x1 = 0
        n_x2 = 0
        local_rotate = rotate
        local_ir = ir
        while local_rotate != want_rotate:
            n_x1 += 1
            local_ir -= 1
            if local_ir < 0 :
                local_ir = 3
            local_rotate = rt[local_ir]
        local_rotate = rotate
        local_ir = ir
        while local_rotate != want_rotate:
            n_x2 += 1
            local_ir += 1
            if local_ir > 3 :
                local_ir = 0
            local_rotate = rt[local_ir]
        best = min(n_x1, n_x2)
    for i in range(best):
        if best == n_x1 :
                move_l(ir,rotate)
        if best == n_x2:
            move_r(ir,rotate)
    return ir , rotate
'''
def Goto(optimized_path,rotate,ir,uid):
    global point_start
    global point_end
    global sleep_time
    points = optimized_path  # Use the passed parameter
    print(points)
    
    point_start=optimized_path[0]
    print(f'point_start: {point_start}')
    
    point_end=optimized_path[len(optimized_path)-1]
    print(f'point_end: {point_end}')
    
    # Check if full_path is valid
    if not points:
        print("Путь не найден")
        return
    # основной цикл
    robot.forward()
    sleep(1)
    gogo()
    all_in = False
           
    print(f'OP: {optimized_path}')
    print(f'CP: {current_path}')

    all_in = any(item in optimized_path for item in current_path)
    print(all_in)  # Вывод: True
    if all_in == True:
        robot.stop()
    
    else:
        robot.forward()
    
'''
        start_y = int(point_start[0])
        start_x = int(point_start[1])
        
        uid_y = int(curent_path[0])
        uid_x = int(curent_path[1])
        
        
        end_y = int(point_end[0])
        end_x = int(point_end[1])
        if start_y != end_y:
            if start_y > uid_y:
                want_rotate = 'верх'
            if start_y < uid_y:
                want_rotate = 'низ'
                
                
                
'''                
'''                
            while rotate != want_rotate:
                robot.right()
                sleep(speeds[0])
                robot.stop()
                print('right')
                ir += 1
                if ir > 3:
                    ir = 0
                rotate = rt[ir]
            move(start_x, start_y,uid,points,point_end)
        elif start_x != end_x:
            if start_x < end_x:
                want_rotate = 'право'
            if start_x > end_x:
                want_rotate = 'лево'
            while rotate != want_rotate:
                robot.right()
                sleep(speeds[0])
                robot.stop()
                print('right')
                ir += 1
                if ir > 3:
                    ir = 0
                rotate = rt[ir]
            move(start_x, start_y,uid,points,point_end)
        sleep(speeds[1])
    #point_start = 0
    #point_end = 1
    
 '''           
#@bot.message_handler(commands=['start'])
def start_welcome(message):
    global points_to_visit
    points_to_visit = []  # Сброс точек при новом запуске
    
    bot.reply_to(message, "Привет давай построим маршрут.",
                 reply_markup=create_keyboard())
    first_point()

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global points_to_visit,optimized_path,sleep_time
        
    if call.data == "add_point":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите строку для точки:",
            reply_markup=create_point_input_keyboard()
        )
        bot.answer_callback_query(call.id)
        
    elif call.data.startswith("row_"):
        row = int(call.data.split("_")[1])
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Выбрана строка {row}. Теперь выберите столбец:",
            reply_markup=create_column_keyboard(row)
        )
        bot.answer_callback_query(call.id)
        
    elif call.data.startswith("point_"):
        parts = call.data.split("_")
        row, col = int(parts[1]), int(parts[2])
        points_to_visit.append((row, col))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Точка ({row}, {col}) добавлена.\nВсего точек: {len(points_to_visit)}",
            reply_markup=create_keyboard()
        )
        bot.answer_callback_query(call.id, f"Точка ({row}, {col}) добавлена")
        
    elif call.data == "cancel_point":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Добавление точки отменено.",
            reply_markup=create_keyboard()
        )
        bot.answer_callback_query(call.id, "Добавление точки отменено")
        
    elif call.data == "find_path":
        global full_path
        if len(points_to_visit) < 2:
            bot.answer_callback_query(call.id, "Добавьте хотя бы 2 точки для поиска пути")
            return
            
        # Поиск пути через все точки
        full_path = path_finder.find_path_through_points(
            points=points_to_visit,
            method='astar'
        )

        if full_path:

            optimized_path = path_finder.optimize_path(full_path)
            print(f"Длина оптимизированного пути: {len(optimized_path)} шагов")


            
            # Отправляем текстовое представление пути
            path_text = format_path_for_telegram(full_path)
            bot.send_message(
                chat_id=call.message.chat.id,
                text=path_text
            )
            
            # Отправляем визуализацию пути
            visualization = visualize_path_for_telegram(full_path, points_to_visit)
            bot.send_message(
                chat_id=call.message.chat.id,
                text=visualization,
                parse_mode="Markdown"
            )
            
            bot.send_message(
            chat_id=call.message.chat.id,
            #message_id=call.message.message_id,
            text="Запустить робота?",
            reply_markup=create_yesno_keyboard()
            )
            bot.answer_callback_query(call.id, "Путь найден!")
        


            
        else:
            bot.answer_callback_query(call.id, "Не удалось найти путь между точками")
    
            
    elif call.data == "show_points":
        if points_to_visit:
            points_text = "Точки для посещения:\n"
            for i, point in enumerate(points_to_visit):
                points_text += f"{i+1}. ({point[0]}, {point[1]})\n"
        else:
            points_text = "Список точек пуст"
            
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=points_text,
            reply_markup=create_keyboard()
        )
        bot.answer_callback_query(call.id)
        
    elif call.data == "reset":
        points_to_visit = []
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Состояние сброшено. Добавьте точки для поиска пути.",
            reply_markup=create_keyboard()
        )
        bot.answer_callback_query(call.id, "Состояние сброшено")
        
    elif call.data == "yes":
        Goto(optimized_path,rotate,ir,uid)
        bot.answer_callback_query(call.id, "Запуск робота")
        
    elif call.data == "no":
        start_welcome()
        bot.answer_callback_query(call.id, "Галя у нас отмена")
        
    elif call.data == "forward":
        robot.forward()
        bot.answer_callback_query(call.id, "Здравое движение(вперед)")
        
    elif call.data == "backward":
        robot.backward()
        bot.answer_callback_query(call.id, "Я стал заднеприводным(еду назад)")
        
    elif call.data == "left":
        robot.left()
        bot.answer_callback_query(call.id, "Налево")
        
    elif call.data == "right":
        robot.right()
        bot.answer_callback_query(call.id, "Направо")
        
    elif call.data == "stop":
        robot.stop()
        bot.answer_callback_query(call.id, "Стою") 
    elif call.data == "calibrovca_yes":
        sleep_time = calibrovca_1
        bot.answer_callback_query(call.id ,'поворот откалиброван')
    elif call.data == "calibrovca_no":
        bot.answer_callback_query(call.id ,'выполните калибровку снова')

bot.infinity_polling()

