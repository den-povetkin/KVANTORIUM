import telebot
from telebot import types
import api_key
#from pico import Robot
#from gpiozero import Motor
from time import sleep

api_key=api_key.api['api_key']
bot=telebot.TeleBot(api_key)

#ADMIN = 19907153
ADMIN = 0

#robot = Robot(left=Motor(23, 24), right=Motor(27, 22))

@bot.message_handler(commands=['id'])
def send_id(message: types.Message):
    # Отправка id
    bot.reply_to(message, text = str(message.chat.id))
    
@bot.message_handler(commands=['start'])
def start(message):
        if message.chat.id == ADMIN:
        #клавиатура
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard = True)
            btn1=types.KeyboardButton('Рассылка')
            btn2=types.KeyboardButton('Управление администраторами')
            btn3=types.KeyboardButton('Управление тренерами')
            btn4=types.KeyboardButton('кнопка')
            markup.add(btn1, btn2, btn3, btn4)
        # отправление клавиатуры с текстом
            bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup) 
        else:
            markup =types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn1 = types.KeyboardButton("Писать текст")
            btn2 = types.KeyboardButton("Рисовать фигуры")
            btn3 = types.KeyboardButton("Калибровка")
            btn4 = types.KeyboardButton("О нас")
            btn5 = types.KeyboardButton("Ручное управление")
            markup.add(btn1, btn2, btn3, btn4, btn5 )
            bot.send_message(message.chat.id, text="Привет, {0.first_name}! Выбирай что будем делать".format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "О нас":
        long_text(message)
    
    elif message.text == "Писать текст":
        bot.send_message(message.chat.id, text="Привет тут будем писать текст")
        
    elif message.text == "Рисовать фигуры":
        bot.send_message(message.chat.id, text="Привет тут будем рисовать фигуры")
        
    elif message.text == "Калибровка":
        bot.send_message(message.chat.id, text="Привет тут будем калибровать шаг робота")
        bot.send_message(message.chat.id, text="Введите шаг робота")
        x = message.text
        #x=int(x)
        Step(x)

    elif message.text == "Ручное управление":
        #bot.send_message(message.chat.id, text="Привет тут будет ручное управление")
        bot.reply_to(message, "Привет! Я робот-Пико. Используй кнопки ниже для управления.",
        reply_markup=create_keyboard())


    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")


def long_text(message): #! отправка длинного сообщения через текстовый файл 
    if message.text == "О нас":
        with open('hi.txt', "r", encoding = "UTF-8") as file:
            data = file.read()
        bot.send_message(message.chat.id, text=data)
#    elif message.text == "Наши услуги":
#        with open('info.txt', "r", encoding = "UTF-8") as file:
#            data = file.read()
#            bot.send_message(message.chat.id, text=data)

def create_keyboard():
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

#@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я робот-Пико. Используй кнопки ниже для управления.",
                 reply_markup=create_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "forward":
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

def Step(x):
    robot.forward()
    sleep(x)
    robot.stop()
def kalibrovka():
    bot.send_message(message.chat.id, text="Введите шаг робота")
    x = int(mesage.text)
    Step(x)
    
bot.infinity_polling()