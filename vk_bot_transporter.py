import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from pico import Robot
from gpiozero import Motor
from time import sleep
from RobotPathFinder import RobotPathFinder
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import threading

# Глобальные переменные
full_path = None
optimized_path = None
calibrovca_1 = 0.57
current_path = []
points_to_visit = []
speeds = []

# Конфигурация VK
VK_TOKEN = "YOUR_VK_GROUP_TOKEN"  # Токен сообщества VK
GROUP_ID = 123456  # ID вашего сообщества

# Инициализация VK
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# Инициализация робота
robot = Robot(left=Motor(23, 24), right=Motor(27, 22))

# Инициализация NFC
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

# Загрузка настроек скорости
try:
    with open('robot_speed.txt', 'r', encoding='utf-8') as file:
        for line in file:
            data = line.split(' ')
            speeds.append(float(data[1]))
except FileNotFoundError:
    speeds = [0.57, 1.0]
    print("Файл настроек не найден, используются значения по умолчанию")

# Параметры окружения
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

# Направления
rt = ['up', 'ri', 'dw', 'lf']
ir = 1
rotate = rt[ir]

def send_message(user_id, text, keyboard=None):
    """Отправка сообщения пользователю"""
    try:
        vk.messages.send(
            user_id=user_id,
            message=text,
            random_id=get_random_id(),
            keyboard=keyboard if keyboard else None
        )
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

def create_main_keyboard():
    """Создание главной клавиатуры"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Задать маршрут", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Показать карту", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Калибровка", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Ручное управление", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("О нас", color=VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()

def create_robot_keyboard():
    """Создание клавиатуры для управления роботом"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("⬆️ Вперед", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("⬇️ Назад", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("⬅️ Налево", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("➡️ Направо", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("🛑 Стоп", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def create_route_keyboard():
    """Создание клавиатуры для построения маршрута"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("➕ Добавить точку", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("🗺 Найти путь", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("📍 Показать точки", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("🔄 Сброс", color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("🔙 Назад", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def create_confirmation_keyboard():
    """Создание клавиатуры подтверждения"""
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("✅ Да", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("❌ Нет", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def long_text(user_id):
    """Отправка длинного сообщения"""
    try:
        with open('hi.txt', "r", encoding="UTF-8") as file:
            data = file.read()
        send_message(user_id, data)
    except FileNotFoundError:
        send_message(user_id, "Информация о нас временно недоступна")

def first_point():
    """Чтение первой NFC метки"""
    global uid, points_to_visit
    
    send_message(user_id, "Поднесите NFC метку для первой точки...")
    
    status = True
    while status:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            text = read_nfc_tag(uid)
            if text:
                try:
                    row = int(text[8])
                    col = int(text[10])
                    points_to_visit.append((row, col))
                    send_message(user_id, f"✅ Точка ({row}, {col}) добавлена!")
                    status = False
                except (IndexError, ValueError):
                    send_message(user_id, "❌ Ошибка чтения координат с метки")
                    status = False
            else:
                send_message(user_id, "❌ Не удалось прочитать данные с метки")
                status = False

def read_nfc_tag(uid):
    """Чтение данных с NFC метки"""
    try:
        if len(uid) == 7:  # NTAG
            text_data = b''
            page_index = 4
            
            for i in range(8):
                try:
                    page_data = pn532.ntag2xx_read_block(page_index + i)
                    if page_data is not None:
                        if b'\x00\x00' in page_data or page_data == b'\x00' * 4:
                            for j, byte in enumerate(page_data):
                                if byte == 0:
                                    text_data += page_data[:j]
                                    break
                            else:
                                text_data += page_data
                            break
                        text_data += page_data
                    else:
                        break
                except Exception as e:
                    print(f"Ошибка чтения: {e}")
                    break
            
            text = text_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
            return text
    except Exception as e:
        print(f"Ошибка: {e}")
    
    return None

def gogo():
    """Чтение NFC меток во время движения"""
    global current_path
    
    uid = pn532.read_passive_target(timeout=1.5)
    if uid is not None:
        text = read_nfc_tag(uid)
        if text:
            try:
                row = int(text[8])
                col = int(text[10])
                new_element = (row, col)
                if new_element not in current_path:
                    current_path.append(new_element)
                print(f"Точка добавлена: {new_element}")
            except (IndexError, ValueError):
                print("Ошибка чтения координат")

def move_robot():
    """Движение робота"""
    global optimized_path, current_path
    
    print('Вперёд')
    robot.forward()
    sleep(1)
    gogo()
    
    all_in = any(item in optimized_path for item in current_path)
    if all_in:
        robot.stop()
        return False
    else:
        return True

def goto_route(user_id):
    """Движение по маршруту"""
    global optimized_path, current_path
    
    if not optimized_path:
        send_message(user_id, "❌ Маршрут не найден")
        return
    
    send_message(user_id, "🚀 Начинаю движение по маршруту...")
    
    for item in optimized_path:
        robot.forward()
        sleep(1)
        gogo()
        
        uid = pn532.read_passive_target(timeout=0.5)
        while uid is None:
            robot.forward()
            sleep(0.5)
            uid = pn532.read_passive_target(timeout=0.5)
        
        robot.stop()
        
        # Поворот к следующей точке
        if optimized_path.index(item) + 1 != len(optimized_path):
            point_start_x = item[0]
            point_start_y = item[1]
            point_end_x = optimized_path[optimized_path.index(item) + 1][0]
            point_end_y = optimized_path[optimized_path.index(item) + 1][1]
            
            if point_start_x < point_end_x or point_start_y > point_end_y:
                robot.right()
            elif point_start_x > point_end_x or point_start_y > point_end_y:
                robot.left()
            
            sleep(speeds[0])
            robot.stop()
    
    send_message(user_id, "✅ Маршрут завершен!")

def format_path_for_vk(path):
    """Форматирование пути для VK"""
    if not path:
        return "❌ Путь не найден"
    
    formatted = "🗺 Найденный путь:\n"
    for i, pos in enumerate(path):
        formatted += f"{i+1}. ({pos[0]}, {pos[1]})\n"
    
    return formatted

def handle_message(user_id, text):
    """Обработка текстовых сообщений"""
    global points_to_visit, optimized_path, current_path
    
    if text == "О нас":
        long_text(user_id)
    
    elif text == "Задать маршрут":
        points_to_visit = []
        current_path = []
        send_message(user_id, "🗺 Построение маршрута", create_route_keyboard())
        threading.Thread(target=first_point, args=(user_id,)).start()
    
    elif text == "Показать карту":
        send_message(user_id, "🔄 Загрузка карты...")
        gogo()
        if current_path:
            send_message(user_id, f"📍 Текущие точки: {current_path}")
        else:
            send_message(user_id, "❌ Нет сохраненных точек")
    
    elif text == "Калибровка":
        send_message(user_id, "⚙️ Введите время поворота в секундах (например, 0.57):")
        # Сохраняем состояние ожидания калибровки
        waiting_for_calibration[user_id] = True
    
    elif text == "Ручное управление":
        send_message(user_id, "🎮 Управление роботом:", create_robot_keyboard())
    
    elif text == "🔙 Назад":
        send_message(user_id, "🏠 Главное меню", create_main_keyboard())
    
    # Кнопки управления роботом
    elif text == "⬆️ Вперед":
        robot.forward()
        send_message(user_id, "⬆️ Движение вперед")
    
    elif text == "⬇️ Назад":
        robot.backward()
        send_message(user_id, "⬇️ Движение назад")
    
    elif text == "⬅️ Налево":
        robot.left()
        send_message(user_id, "⬅️ Поворот налево")
    
    elif text == "➡️ Направо":
        robot.right()
        send_message(user_id, "➡️ Поворот направо")
    
    elif text == "🛑 Стоп":
        robot.stop()
        send_message(user_id, "🛑 Стоп")
    
    # Кнопки построения маршрута
    elif text == "➕ Добавить точку":
        send_message(user_id, "🔄 Поднесите NFC метку для добавления точки...")
        threading.Thread(target=first_point, args=(user_id,)).start()
    
    elif text == "🗺 Найти путь":
        if len(points_to_visit) < 2:
            send_message(user_id, "❌ Добавьте хотя бы 2 точки для поиска пути")
            return
        
        full_path = path_finder.find_path_through_points(
            points=points_to_visit,
            method='astar'
        )
        
        if full_path:
            optimized_path = path_finder.optimize_path(full_path)
            path_text = format_path_for_vk(full_path)
            send_message(user_id, path_text)
            send_message(user_id, "🚀 Запустить робота по маршруту?", create_confirmation_keyboard())
        else:
            send_message(user_id, "❌ Не удалось найти путь между точками")
    
    elif text == "📍 Показать точки":
        if points_to_visit:
            points_text = "📍 Точки для посещения:\n"
            for i, point in enumerate(points_to_visit):
                points_text += f"{i+1}. ({point[0]}, {point[1]})\n"
            send_message(user_id, points_text)
        else:
            send_message(user_id, "📭 Список точек пуст")
    
    elif text == "🔄 Сброс":
        points_to_visit = []
        current_path = []
        send_message(user_id, "🔄 Состояние сброшено. Добавьте точки для поиска пути.")
    
    # Подтверждение
    elif text == "✅ Да":
        threading.Thread(target=goto_route, args=(user_id,)).start()
    
    elif text == "❌ Нет":
        send_message(user_id, "❌ Запуск отменен", create_route_keyboard())

# Словари для хранения состояний пользователей
waiting_for_calibration = {}
waiting_for_coordinates = {}

def main():
    """Основной цикл обработки сообщений"""
    print("Бот запущен и ожидает сообщения...")
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.message.text:
                user_id = event.message.from_id
                text = event.message.text
                
                # Проверяем ожидание калибровки
                if waiting_for_calibration.get(user_id):
                    try:
                        calib_time = float(text)
                        global calibrovca_1, speeds
                        calibrovca_1 = calib_time
                        robot.right()
                        sleep(calib_time)
                        robot.stop()
                        send_message(user_id, f"✅ Калибровка завершена! Время поворота: {calib_time} сек")
                        waiting_for_calibration[user_id] = False
                    except ValueError:
                        send_message(user_id, "❌ Пожалуйста, введите число")
                    continue
                
                # Обрабатываем обычное сообщение
                handle_message(user_id, text)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nБот остановлен")
        robot.stop()