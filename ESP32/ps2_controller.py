# ps2_controller.py
"""
Библиотека для работы с геймпадом PS2 на ESP32 (MicroPython)
Основана на протоколе с gamesx.com
"""

import machine
import time
from micropython import const

# Константы протокола PS2
PSX_ID_DIGITAL = const(0x41)
PSX_ID_ANALOG_RED = const(0x73)
PSX_ID_ANALOG_GREEN = const(0x53)
PSX_ID_NEGCON = const(0x23)
PSX_ID_MOUSE = const(0x12)

# Команды
CMD_POLL = const(0x42)
CMD_ENTER_CONFIG = const(0x43)
CMD_SET_MODE = const(0x44)
CMD_EXIT_CONFIG = const(0x43)  # С другим набором параметров

class PS2Controller:
    """Класс для работы с геймпадом PS2 на ESP32"""
    
    def __init__(self, pin_clk=18, pin_cmd=23, pin_att=14, pin_dat=19, pin_ack=None):
        """
        Инициализация контроллера PS2
        
        Args:
            pin_clk: Пин для CLOCK (GPIO номер)
            pin_cmd: Пин для COMMAND
            pin_att: Пин для ATT/CS
            pin_dat: Пин для DATA
            pin_ack: Пин для ACK (опционально)
        """
        # Настройка пинов
        self.clk = machine.Pin(pin_clk, machine.Pin.OUT)
        self.cmd = machine.Pin(pin_cmd, machine.Pin.OUT)
        self.att = machine.Pin(pin_att, machine.Pin.OUT)
        self.dat = machine.Pin(pin_dat, machine.Pin.IN, machine.Pin.PULL_UP)
        
        # ACK опционально
        self.ack = None
        if pin_ack is not None:
            self.ack = machine.Pin(pin_ack, machine.Pin.IN, machine.Pin.PULL_UP)
        
        # Начальные состояния
        self.clk.value(1)  # CLK изначально высокий
        self.cmd.value(1)
        self.att.value(1)  # ATT изначально высокий (не активен)
        
        # Состояние контроллера
        self.controller_type = 0
        self.analog_mode = False
        self.connected = False
        
        # Данные кнопок
        self.buttons = {
            'select': False, 'start': False,
            'up': False, 'right': False, 'down': False, 'left': False,
            'triangle': False, 'circle': False, 'cross': False, 'square': False,
            'l1': False, 'l2': False, 'r1': False, 'r2': False,
            'l3': False, 'r3': False
        }
        
        # Аналоговые значения (0-255, 128=центр)
        self.analog = {
            'rx': 128, 'ry': 128,  # Правый стик
            'lx': 128, 'ly': 128   # Левый стик
        }
        
        print(f"PS2Controller инициализирован на пинах:")
        print(f"  CLK: GPIO{self.clk}, CMD: GPIO{self.cmd}")
        print(f"  ATT: GPIO{self.att}, DAT: GPIO{self.dat}")
        if self.ack:
            print(f"  ACK: GPIO{self.ack}")
    
    def _clock_tick(self):
        """Генерация тактового импульса"""
        self.clk.value(0)
        time.sleep_us(5)  # Минимальная задержка
        self.clk.value(1)
        time.sleep_us(5)
    
    def _send_byte(self, byte):
        """
        Отправка одного байта на геймпад
        и одновременное чтение ответа
        
        Returns:
            Полученный байт данных
        """
        response = 0
        
        # Отправляем 8 бит, LSB first
        for i in range(8):
            # Устанавливаем бит COMMAND
            bit_to_send = (byte >> i) & 0x01
            self.cmd.value(bit_to_send)
            
            # Ждем установления сигнала
            time.sleep_us(2)
            
            # Тактовый импульс (падение фронта)
            self.clk.value(0)
            time.sleep_us(2)
            
            # Читаем DATA на поднимающемся фронте
            if self.dat.value():
                response |= (1 << i)
            
            # Завершаем такт
            self.clk.value(1)
            time.sleep_us(2)
        
        return response
    
    def _transmit(self, cmd_bytes, read_response=True):
        """
        Передача пакета геймпаду
        
        Args:
            cmd_bytes: Список байтов для отправки
            read_response: Читать ли ответ
            
        Returns:
            Список полученных байтов
        """
        response = []
        
        # Активируем геймпад (ATT в LOW)
        self.att.value(0)
        time.sleep_us(10)
        
        # Отправляем все байты команды
        for i, byte in enumerate(cmd_bytes):
            rx_byte = self._send_byte(byte)
            
            # Сохраняем ответ (если требуется и это не первый байт)
            if read_response and i > 0:
                response.append(rx_byte)
        
        # Деактивируем геймпад
        self.att.value(1)
        time.sleep_us(10)
        
        return response
    
    def initialize(self):
        """Инициализация и определение типа геймпада"""
        print("Поиск геймпада PS2...")
        
        # 1. Пробуем определить контроллер
        response = self._transmit([0x01, 0x42, 0x00])
        
        if not response or len(response) < 1:
            print("Нет ответа от геймпада!")
            return False
        
        self.controller_type = response[0]
        
        # Определяем тип контроллера
        types = {
            PSX_ID_DIGITAL: "Цифровой",
            PSX_ID_ANALOG_RED: "Аналоговый (красный)",
            PSX_ID_ANALOG_GREEN: "Аналоговый (зеленый)",
            PSX_ID_NEGCON: "NegCon",
            PSX_ID_MOUSE: "Мышь"
        }
        
        type_name = types.get(self.controller_type, f"Неизвестный (0x{self.controller_type:02X})")
        print(f"Найден: {type_name}")
        
        # 2. Для аналоговых геймпадов включаем аналоговый режим
        if self.controller_type in [PSX_ID_ANALOG_RED, PSX_ID_ANALOG_GREEN]:
            print("Включение аналогового режима...")
            
            # Вход в режим конфигурации
            self._transmit([0x01, 0x43, 0x00, 0x01, 0x00])
            time.sleep_ms(10)
            
            # Включение аналогового режима
            self._transmit([0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00])
            time.sleep_ms(10)
            
            # Выход из режима конфигурации
            self._transmit([0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A])
            time.sleep_ms(10)
            
            self.analog_mode = True
        
        self.connected = True
        return True
    
    def poll(self):
        """Опрос геймпада и обновление состояния"""
        if not self.connected:
            return False
        
        # Отправляем команду опроса
        response = self._transmit([0x01, 0x42, 0x00])
        
        if len(response) < 2:
            print("Ошибка при опросе геймпада")
            return False
        
        # Проверяем ID
        if response[0] != self.controller_type:
            print(f"ID изменился: 0x{response[0]:02X} (было 0x{self.controller_type:02X})")
            self.controller_type = response[0]
        
        # Проверяем 0x5A
        if response[1] != 0x5A:
            print(f"Нет 0x5A: 0x{response[1]:02X}")
        
        # Читаем оставшиеся данные
        # Для этого снова активируем ATT
        self.att.value(0)
        time.sleep_us(10)
        
        # Уже отправили 0x01, 0x42, 0x00
        # Просто читаем данные
        data_bytes = []
        bytes_to_read = 6 if self.analog_mode else 2
        
        for i in range(bytes_to_read):
            rx_byte = self._send_byte(0x00)
            data_bytes.append(rx_byte)
        
        self.att.value(1)
        
        # Объединяем все данные
        all_data = response + data_bytes
        
        # Парсим данные
        self._parse_data(all_data)
        
        return True
    
    def _parse_data(self, data):
        """Парсинг данных в зависимости от типа контроллера"""
        if len(data) < 5:
            return
        
        byte4 = data[3]
        byte5 = data[4]
        
        # Общие кнопки для всех типов
        self.buttons['select'] = not bool(byte4 & 0x01)
        self.buttons['start'] = not bool(byte4 & 0x08)
        self.buttons['up'] = not bool(byte4 & 0x10)
        self.buttons['right'] = not bool(byte4 & 0x20)
        self.buttons['down'] = not bool(byte4 & 0x40)
        self.buttons['left'] = not bool(byte4 & 0x80)
        
        # Основные кнопки
        self.buttons['l2'] = not bool(byte5 & 0x01)
        self.buttons['r2'] = not bool(byte5 & 0x02)
        self.buttons['l1'] = not bool(byte5 & 0x04)
        self.buttons['r1'] = not bool(byte5 & 0x08)
        self.buttons['triangle'] = not bool(byte5 & 0x10)
        self.buttons['circle'] = not bool(byte5 & 0x20)
        self.buttons['cross'] = not bool(byte5 & 0x40)
        self.buttons['square'] = not bool(byte5 & 0x80)
        
        # Для аналоговых геймпадов
        if self.analog_mode and len(data) >= 9:
            # L3 и R3
            self.buttons['l3'] = not bool(byte4 & 0x02)
            self.buttons['r3'] = not bool(byte4 & 0x04)
            
            # Аналоговые стики
            self.analog['rx'] = data[5]  # Right X
            self.analog['ry'] = data[6]  # Right Y
            self.analog['lx'] = data[7]  # Left X
            self.analog['ly'] = data[8]  # Left Y
    
    def get_button(self, name):
        """Получить состояние кнопки по имени"""
        return self.buttons.get(name, False)
    
    def get_analog(self, axis):
        """Получить значение аналоговой оси"""
        return self.analog.get(axis, 128)
    
    def print_state(self):
        """Вывод состояния геймпада"""
        print("\n" + "="*50)
        print("Состояние геймпада PS2")
        print("="*50)
        
        # Кнопки
        print("Кнопки:")
        btn_names = ['select', 'start', 'up', 'right', 'down', 'left',
                    'triangle', 'circle', 'cross', 'square',
                    'l1', 'l2', 'r1', 'r2', 'l3', 'r3']
        
        for i, name in enumerate(btn_names):
            state = "●" if self.buttons[name] else "○"
            print(f"{name:8}: {state}", end="  ")
            if (i + 1) % 4 == 0:
                print()
        print()
        
        # Аналоговые стики
        if self.analog_mode:
            print("Аналоговые стики:")
            print(f"  Левый:  X={self.analog['lx']:3d} Y={self.analog['ly']:3d}")
            print(f"  Правый: X={self.analog['rx']:3d} Y={self.analog['ry']:3d}")
            
            # Графическое представление
            print("  График:")
            for axis, value in self.analog.items():
                bar = self._create_bar(value)
                print(f"    {axis}: {bar} ({value})")
        else:
            print("Аналоговый режим: отключен")
        
        print("="*50)
    
    def _create_bar(self, value):
        """Создать графическую шкалу"""
        length = 20
        center = 128
        
        if value < center:
            pos = int((center - value) / center * (length // 2))
            pos = min(pos, length // 2)
            bar = "[" + " " * (length//2 - pos) + "<" + "=" * (pos-1) + " " * (length//2) + "]"
        elif value > center:
            pos = int((value - center) / (255 - center) * (length // 2))
            pos = min(pos, length // 2)
            bar = "[" + " " * (length//2) + "=" * (pos-1) + ">" + " " * (length//2 - pos) + "]"
        else:
            bar = "[" + " " * (length//2) + "|" + " " * (length//2) + "]"
        
        return bar

# ============================================================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ============================================================================

# Пример 1: Базовый тест
def test_basic():
    """Простой тест подключения"""
    print("Тест подключения PS2 к ESP32")
    
    # Инициализация (используем стандартные пины SPI VSPI)
    ps2 = PS2Controller(
        pin_clk=18,    # SCK
        pin_cmd=23,    # MOSI
        pin_att=14,    # CS
        pin_dat=19,    # MISO
        pin_ack=27     # ACK (опционально)
    )
    
    # Инициализация геймпада
    if not ps2.initialize():
        print("Ошибка инициализации геймпада!")
        return
    
    print("Геймпад инициализирован успешно!")
    
    # Бесконечный цикл опроса
    counter = 0
    try:
        while True:
            if ps2.poll():
                # Выводим состояние каждые 10 опросов
                if counter % 10 == 0:
                    ps2.print_state()
                
                # Проверка конкретных кнопок
                if ps2.get_button('triangle'):
                    print("Нажата TRIANGLE!")
                if ps2.get_button('start') and ps2.get_button('select'):
                    print("Комбинация START+SELECT - выход")
                    break
                
                counter += 1
            else:
                print("Ошибка опроса")
            
            time.sleep_ms(50)  # 20 Гц
    
    except KeyboardInterrupt:
        print("\nТест завершен")
    
    print("Всего опросов:", counter)

# Пример 2: Управление светодиодом
def led_control():
    """Управление светодиодом с помощью геймпада"""
    from machine import Pin, PWM
    
    print("Управление светодиодом с геймпада PS2")
    
    # Настройка светодиода (GPIO2 на многих ESP32)
    led = PWM(Pin(2), freq=1000)
    
    # Инициализация геймпада
    ps2 = PS2Controller(pin_clk=18, pin_cmd=23, pin_att=14, pin_dat=19)
    
    if not ps2.initialize():
        print("Ошибка инициализации геймпада!")
        return
    
    print("Управление:")
    print("  Крестовина вверх/вниз - яркость")
    print("  Круг/Крест - вкл/выкл")
    print("  SELECT+START - выход")
    
    brightness = 512  # 0-1023
    
    try:
        while True:
            if ps2.poll():
                # Управление яркостью
                if ps2.get_button('up'):
                    brightness = min(1023, brightness + 10)
                    led.duty(brightness)
                    print(f"Яркость: {brightness}")
                
                if ps2.get_button('down'):
                    brightness = max(0, brightness - 10)
                    led.duty(brightness)
                    print(f"Яркость: {brightness}")
                
                # Вкл/выкл
                if ps2.get_button('circle'):
                    led.duty(1023)
                    print("Светодиод ВКЛ")
                    time.sleep_ms(200)  # Защита от дребезга
                
                if ps2.get_button('cross'):
                    led.duty(0)
                    print("Светодиод ВЫКЛ")
                    time.sleep_ms(200)
                
                # Выход
                if ps2.get_button('select') and ps2.get_button('start'):
                    print("Выход")
                    break
                
                # Управление через аналоговые стики (если есть)
                if ps2.analog_mode:
                    rx = ps2.get_analog('rx')
                    if rx < 100:  # Стик влево
                        led.duty(led.duty() // 2)
                    elif rx > 150:  # Стик вправо
                        led.duty(min(1023, led.duty() * 2))
            
            time.sleep_ms(20)
    
    finally:
        led.duty(0)  # Выключить светодиод

# Пример 3: Отправка данных по Bluetooth/UART
def ps2_to_serial():
    """Отправка данных геймпада по UART"""
    import ujson
    from machine import UART
    
    print("PS2 -> UART транслятор")
    
    # Настройка UART (например, для Bluetooth модуля HC-05)
    uart = UART(2, baudrate=9600, tx=17, rx=16)
    
    # Инициализация геймпада
    ps2 = PS2Controller()
    
    if not ps2.initialize():
        print("Ошибка инициализации геймпада!")
        return
    
    print("Отправка данных по UART...")
    print("Формат: JSON с состоянием кнопок и осей")
    
    try:
        while True:
            if ps2.poll():
                # Создаем словарь с данными
                data = {
                    'buttons': ps2.buttons,
                    'analog': ps2.analog,
                    'timestamp': time.ticks_ms()
                }
                
                # Конвертируем в JSON
                json_data = ujson.dumps(data)
                
                # Отправляем по UART
                uart.write(json_data + '\n')
                
                # Выводим в консоль для отладки
                print(f"Отправлено: {len(json_data)} байт")
                
                # Пауза между отправками
                time.sleep_ms(50)
    
    except KeyboardInterrupt:
        print("\nОстановка трансляции")

# Пример 4: Веб-сервер для мониторинга
def web_server():
    """Веб-сервер для мониторинга состояния геймпада"""
    import network
    import socket
    import ujson
    
    # Подключение к WiFi
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('SSID', 'PASSWORD')  # Замените на свои данные
    
    while not sta_if.isconnected():
        time.sleep_ms(100)
    
    print(f"Подключено к WiFi. IP: {sta_if.ifconfig()[0]}")
    
    # Инициализация геймпада
    ps2 = PS2Controller()
    ps2.initialize()
    
    # Создание сокета
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    
    print(f"Веб-сервер запущен на http://{sta_if.ifconfig()[0]}:80")
    
    # HTML страница
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>PS2 Controller Monitor</title>
        <meta http-equiv="refresh" content="0.5">
        <style>
            body { font-family: Arial; margin: 20px; }
            .button { display: inline-block; padding: 10px; margin: 5px; border: 1px solid #ccc; }
            .pressed { background-color: #4CAF50; color: white; }
            .analog { margin: 10px 0; }
            .bar { width: 200px; height: 20px; background: #ddd; display: inline-block; }
            .fill { height: 100%; background: #2196F3; }
        </style>
    </head>
    <body>
        <h1>PS2 Controller Monitor</h1>
        <div id="data">Loading...</div>
    </body>
    </html>"""
    
    try:
        while True:
            # Опрос геймпада
            ps2.poll()
            
            # Обработка подключений
            cl, addr = s.accept()
            cl_file = cl.makefile('rwb', 0)
            
            # Читаем запрос
            request = cl_file.readline()
            while True:
                line = cl_file.readline()
                if not line or line == b'\r\n':
                    break
            
            # Создаем JSON с данными
            data = {
                'buttons': ps2.buttons,
                'analog': ps2.analog,
                'connected': ps2.connected
            }
            
            json_data = ujson.dumps(data)
            
            # Отправляем ответ
            cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
            cl.send(json_data)
            cl.close()
            
            time.sleep_ms(10)
    
    except Exception as e:
        print(f"Ошибка: {e}")

# ============================================================================
# ТЕСТОВЫЙ СКРИПТ
# ============================================================================

def main_test():
    """Основной тестовый скрипт"""
    print("="*60)
    print("ТЕСТ ГЕЙМПАДА PS2 НА ESP32 (MicroPython)")
    print("="*60)
    print()
    
    # Выбор примера
    print("Выберите пример:")
    print("1. Базовый тест (вывод в консоль)")
    print("2. Управление светодиодом")
    print("3. Отправка данных по UART")
    print("4. Веб-сервер мониторинга")
    print()
    
    try:
        choice = input("Введите номер (1-4): ").strip()
        
        if choice == '1':
            test_basic()
        elif choice == '2':
            led_control()
        elif choice == '3':
            ps2_to_serial()
        elif choice == '4':
            web_server()
        else:
            print("Неверный выбор")
    
    except KeyboardInterrupt:
        print("\nПрограмма завершена")
    except Exception as e:
        print(f"Ошибка: {e}")

# Запуск при импорте как модуля
if __name__ == "__main__":
    main_test()