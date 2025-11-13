import telebot
from telebot import types
from gpiozero import AngularServo
from time import sleep
import api_key


api_key=api_key.api['api_key']
bot=telebot.TeleBot(api_key)




motorL = AngularServo(24, min_angle=-90, max_angle=90)
#motorR = AngularServo(26, min_angle=-90, max_angle=90)
motorL.detach()
#motorR.detach()

def forvard():
    motorL.angle = 90
    #motorR.angle(-90)
    
def back():
    motorL.angle= - 90
    #motorR.angle(90)
    
def left():
    motorL.angle = 90
    motorR.angle = 90
    
def right():
    motorL.angle = -90
    motorR.angle = -90
    
def stop():
    motorL.detach()
    #motorR.detach()

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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я робот-Пико. Используй кнопки ниже для управления.",
                 reply_markup=create_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "forward":
        forvard()
        bot.answer_callback_query(call.id, "Здравое движение(вперед)")
    elif call.data == "backward":
        back()
        bot.answer_callback_query(call.id, "Я стал заднеприводным(еду назад)")
    elif call.data == "left":
        left()
        bot.answer_callback_query(call.id, "Налево")
    elif call.data == "right":
        right()
        bot.answer_callback_query(call.id, "Направо")
    elif call.data == "stop":
        stop()
        bot.answer_callback_query(call.id, "Стою")

bot.polling()
