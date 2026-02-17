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

api_key=api_key.api['api_key']
bot=telebot.TeleBot(api_key)

#ADMIN = 19907153
ADMIN = 0

robot = Robot(left=Motor(23, 24), right=Motor(27, 22))

# Инициализация I2C
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Настройка PN532
pn532.SAM_configuration()

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
        search_point()

        
    elif message.text == "Калибровка":
        bot.send_message(message.chat.id, text="Привет тут будем калибровать шаг робота")
        #bot.send_message(message.chat.id, text="Введите шаг робота")
        #bot.register_next_step_handler(message,Step)


    elif message.text == "Ручное управление":
        bot.send_message(message.chat.id, text="Привет тут будет ручное управление")
        bot.reply_to(message, "Привет! Я робот-Пико. Используй кнопки ниже для управления.",
        reply_markup=create_robot_keyboard())


    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")


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
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
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
    print("Ожидание NFC метки...")
    print("Поднесите карту к считывателю")
    uid = ''
    status = True
    while status == True:
        # Проверка наличия карты
        uid = pn532.read_passive_target(timeout=0.5)
        
        if uid is not None:
            status = False
            cid=[hex(i) for i in uid]
            cidx=str(cid[0])
            cidy=str(cid[1])
        
            row, col = int(cidx[2]), int(cidy[2])
            points_to_visit.append((row, col))
          
            print('Текущая координата', cidx[2],cidy[2])
            print(points_to_visit)
    
def search_point():
    
    print("Ожидание NFC метки...")
    status = True
    while status == True:
        # Проверка наличия карты
        uid = pn532.read_passive_target(timeout=0.5)
        
        if uid is not None:
            status = False
            cid=[hex(i) for i in uid]
            cidx=str(cid[0])
            cidy=str(cid[1])
            
            row=int(cidx[2])
            col=int(cidy[2])
                    
            print(f'Текущая координата {row},{col}')
    return row, col
            
#@bot.message_handler(commands=['start'])
def start_welcome(message):
    global points_to_visit
    points_to_visit = []  # Сброс точек при новом запуске
    
    bot.reply_to(message, "Привет! Я робот-Пико. Используй кнопки ниже для управления.",
                 reply_markup=create_keyboard())
    first_point()

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global points_to_visit
        
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
        if len(points_to_visit) < 2:
            bot.answer_callback_query(call.id, "Добавьте хотя бы 2 точки для поиска пути")
            return
            
        # Поиск пути через все точки
        full_path = path_finder.find_path_through_points(
            points=points_to_visit,
            method='astar'
        )
        
        if full_path:
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

bot.infinity_polling()

