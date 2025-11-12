import telebot
from telebot import types
from time import sleep
import api_key
from pico import Robot
from gpiozero import Motor


api_key=api_key.api['api_key']
bot=telebot.TeleBot(api_key)

robot = Robot(left=Motor(23, 24), right=Motor(27, 22))

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

bot.polling()