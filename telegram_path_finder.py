import telebot
from telebot import types
import api_key
from poisk_puti2 import RobotPathFinder

# Инициализация бота
api_key = api_key.api['api_key']
bot = telebot.TeleBot(api_key)

# Глобальные переменные для хранения состояния
path_finder = None
environment = None
points_to_visit = []
current_point_index = 0

def initialize_environment():
    """Инициализация среды по умолчанию"""
    global environment, path_finder
    environment = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]
    
    path_finder = RobotPathFinder(
        matrix=environment,
        obstacles=[1],
        allow_diagonal=False,
        robot_size=1
    )

def create_main_keyboard():
    """Создание основной клавиатуры"""
    keyboard = types.InlineKeyboardMarkup()
    
    add_point_btn = types.InlineKeyboardButton(text="Добавить точку", callback_data="add_point")
    find_path_btn = types.InlineKeyboardButton(text="Найти путь", callback_data="find_path")
    show_points_btn = types.InlineKeyboardButton(text="Показать точки", callback_data="show_points")
    reset_btn = types.InlineKeyboardButton(text="Сброс", callback_data="reset")
    
    keyboard.add(add_point_btn, find_path_btn)
    keyboard.add(show_points_btn, reset_btn)
    
    return keyboard

def create_point_input_keyboard():
    """Создание клавиатуры для ввода координат точки"""
    keyboard = types.InlineKeyboardMarkup()
    
    # Создаем кнопки для строк (0-9)
    row_buttons = []
    for i in range(10):
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
    for i in range(10):
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
    if not path_finder:
        return "Планировщик пути не инициализирован"
    
    # Используем существующий метод визуализации
    visualization = path_finder.visualize_path(path=path, points=points)
    return f"Визуализация пути:\n```\n{visualization}\n```"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    global points_to_visit
    points_to_visit = []  # Сброс точек при новом запуске
    initialize_environment()  # Инициализация среды
    
    bot.reply_to(message, 
                 "Привет! Я бот для поиска пути робота. Используй кнопки ниже для управления.",
                 reply_markup=create_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    """Обработчик callback-запросов"""
    global points_to_visit, current_point_index
    
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
            reply_markup=create_main_keyboard()
        )
        bot.answer_callback_query(call.id, f"Точка ({row}, {col}) добавлена")
        
    elif call.data == "cancel_point":
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Добавление точки отменено.",
            reply_markup=create_main_keyboard()
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
            reply_markup=create_main_keyboard()
        )
        bot.answer_callback_query(call.id)
        
    elif call.data == "reset":
        points_to_visit = []
        initialize_environment()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Состояние сброшено. Добавьте точки для поиска пути.",
            reply_markup=create_main_keyboard()
        )
        bot.answer_callback_query(call.id, "Состояние сброшено")

if __name__ == "__main__":
    # Инициализация среды при запуске
    initialize_environment()
    # Запуск бота
    bot.polling()
