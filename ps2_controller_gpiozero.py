#!/usr/bin/env python3
"""
PS2 Controller Library for Raspberry Pi using gpiozero
Поддерживает геймпады SZDoit и аналогичные
"""

from gpiozero import DigitalInputDevice, DigitalOutputDevice
import time
import threading
from collections import deque

class PS2ControllerGPIOZero:
    # Константы кнопок
    BUTTON_SELECT   = 0
    BUTTON_L3       = 1
    BUTTON_R3       = 2
    BUTTON_START    = 3
    BUTTON_UP       = 4
    BUTTON_RIGHT    = 5
    BUTTON_DOWN     = 6
    BUTTON_LEFT     = 7
    BUTTON_L2       = 8
    BUTTON_R2       = 9
    BUTTON_L1       = 10
    BUTTON_R1       = 11
    BUTTON_TRIANGLE = 12
    BUTTON_CIRCLE   = 13
    BUTTON_CROSS    = 14
    BUTTON_SQUARE   = 15
    
    # Названия кнопок для вывода
    BUTTON_NAMES = {
        0: "SELECT", 1: "L3", 2: "R3", 3: "START",
        4: "UP", 5: "RIGHT", 6: "DOWN", 7: "LEFT",
        8: "L2", 9: "R2", 10: "L1", 11: "R1",
        12: "TRIANGLE", 13: "CIRCLE", 14: "CROSS", 15: "SQUARE"
    }
    
    # Режимы аналоговых стиков
    MODE_DIGITAL = 0x41
    MODE_ANALOG = 0x73
    MODE_CONFIG = 0xF0
    
    def __init__(self, data_pin=17, cmd_pin=18, att_pin=27, clk_pin=22, 
                 polling_rate=50, auto_init=True):
        """
        Инициализация контроллера PS2
        
        Args:
            data_pin: GPIO для данных (DATA)
            cmd_pin: GPIO для команд (CMD)
            att_pin: GPIO для выбора (ATT/CS)
            clk_pin: GPIO для тактового сигнала (CLK)
            polling_rate: частота опроса в Гц
            auto_init: автоматическая инициализация при запуске
        """
        # Сохраняем параметры
        self.data_pin = data_pin
        self.cmd_pin = cmd_pin
        self.att_pin = att_pin
        self.clk_pin = clk_pin
        
        # Инициализируем пины через gpiozero
        self.data = DigitalInputDevice(data_pin, pull_up=True)
        self.cmd = DigitalOutputDevice(cmd_pin, initial_value=False)
        self.att = DigitalOutputDevice(att_pin, initial_value=True)
        self.clk = DigitalOutputDevice(clk_pin, initial_value=True)
        
        # Состояние контроллера
        self.button_state = [False] * 16
        self.button_pressed = [False] * 16
        self.button_released = [False] * 16
        self.analog_state = {
            'lx': 128, 'ly': 128,  # Левый стик
            'rx': 128, 'ry': 128,  # Правый стик
            'l2': 0, 'r2': 0       # Аналоговые триггеры
        }
        
        # Флаги
        self.connected = False
        self.analog_mode = False
        self.config_mode = False
        self.running = False
        
        # Очередь для плавного вывода
        self.output_queue = deque(maxlen=10)
        
        # Управление потоками
        self.polling_thread = None
        self.polling_rate = polling_rate
        self.polling_interval = 1.0 / polling_rate
        
        # Статистика
        self.read_count = 0
        self.error_count = 0
        
        # Автоматическая инициализация
        if auto_init:
            self.initialize()
    
    def initialize(self):
        """Инициализация контроллера"""
        try:
            print(f"[INFO] Инициализация PS2 контроллера на пинах:")
            print(f"       DATA: GPIO{self.data_pin}, CMD: GPIO{self.cmd_pin}")
            print(f"       ATT:  GPIO{self.att_pin}, CLK: GPIO{self.clk_pin}")
            
            # Даем время на стабилизацию питания
            time.sleep(0.1)
            
            # Сбрасываем контроллер
            self._reset_controller()
            
            # Проверяем подключение
            self.connected = self._check_connection()
            
            if self.connected:
                print("[INFO] Контроллер PS2 подключен")
                
                # Включаем аналоговый режим
                self._enter_analog_mode()
                self.analog_mode = True
                print("[INFO] Аналоговый режим активирован")
                
                # Запускаем поток опроса
                self.start_polling()
                return True
            else:
                print("[ERROR] Контроллер PS2 не обнаружен")
                return False
                
        except Exception as e:
            print(f"[ERROR] Ошибка инициализации: {e}")
            return False
    
    def _send_byte(self, byte):
        """Отправка байта контроллеру"""
        response = 0
        
        for i in range(8):
            # Устанавливаем бит CMD
            bit = (byte >> i) & 0x01
            self.cmd.value = bit
            
            # Тактовый импульс
            self.clk.value = False
            time.sleep(0.00001)  # 10µs
            
            # Читаем бит данных
            response_bit = self.data.value
            if response_bit:
                response |= (1 << i)
            
            # Завершаем такт
            self.clk.value = True
            time.sleep(0.00001)  # 10µs
        
        return response
    
    def _read_command(self, command, bytes_to_read=1):
        """Отправка команды и чтение ответа"""
        responses = []
        
        # Активируем контроллер
        self.att.value = False
        time.sleep(0.0001)  # 100µs
        
        try:
            # Отправляем команду
            responses.append(self._send_byte(command))
            
            # Читаем остальные байты
            for _ in range(bytes_to_read - 1):
                responses.append(self._send_byte(0x00))
                
        finally:
            # Деактивируем контроллер
            self.att.value = True
        
        return responses
    
    def _check_connection(self):
        """Проверка подключения контроллера"""
        try:
            # Отправляем команду идентификации
            response = self._read_command(0x01, 5)
            
            # Проверяем ответ
            if len(response) >= 5 and response[0] == 0x73 and response[1] == 0x5A:
                print(f"[INFO] ID контроллера: {[hex(x) for x in response]}")
                return True
            else:
                print(f"[WARN] Неожиданный ответ: {[hex(x) for x in response]}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Ошибка проверки подключения: {e}")
            return False
    
    def _reset_controller(self):
        """Сброс контроллера"""
        print("[INFO] Сброс контроллера...")
        
        # Последовательность сброса
        self.att.value = True
        self.clk.value = True
        self.cmd.value = False
        time.sleep(0.01)
        
        # Активируем и деактивируем контроллер
        self.att.value = False
        time.sleep(0.01)
        self.att.value = True
        time.sleep(0.1)
    
    def _enter_analog_mode(self):
        """Включение аналогового режима"""
        try:
            # Входим в конфигурационный режим
            self._read_command(0x01, 5)  # ID
            self._read_command(0x43, 5)  # Enter config
            
            # Включаем аналоговый режим
            self._read_command(0x44, 5)  # Set mode
            self._read_command(0x01, 5)  # Analog lock
            self._read_command(0x03, 5)  # Analog mode
            
            # Выходим из конфигурационного режима
            self._read_command(0x43, 5)  # Exit config
            self._read_command(0x01, 5)  # Analog mode on
            
            time.sleep(0.1)  # Даем время на переключение
            
        except Exception as e:
            print(f"[ERROR] Ошибка включения аналогового режима: {e}")
    
    def _update_controller_state(self):
        """Обновление состояния контроллера"""
        try:
            # Читаем данные контроллера
            data = self._read_command(0x42, 9)
            
            if len(data) >= 9:
                self.read_count += 1
                
                # Обрабатываем кнопки (первые 2 байта)
                self._process_buttons(data[0], data[1])
                
                # Обрабатываем аналоговые значения (остальные байты)
                self._process_analog(data[2:])
                
                return True
            else:
                self.error_count += 1
                return False
                
        except Exception as e:
            self.error_count += 1
            if self.error_count % 50 == 0:  # Выводим не чаще
                print(f"[ERROR] Ошибка чтения: {e}")
            return False
    
    def _process_buttons(self, byte1, byte2):
        """Обработка состояния кнопок"""
        new_state = []
        
        # Байт 1: RIGHT, LEFT, DOWN, UP, START, R3, L3, SELECT
        mask1 = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
        
        # Байт 2: SQUARE, CROSS, CIRCLE, TRIANGLE, R1, L1, R2, L2
        mask2 = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
        
        # Читаем первый байт (инвертированная логика: 0 = нажата)
        for i in range(8):
            new_state.append((byte1 & mask1[i]) == 0)
        
        # Читаем второй байт
        for i in range(8):
            new_state.append((byte2 & mask2[i]) == 0)
        
        # Обновляем состояния нажатия/отпускания
        for i in range(16):
            old_state = self.button_state[i]
            self.button_state[i] = new_state[i]
            self.button_pressed[i] = (not old_state and new_state[i])
            self.button_released[i] = (old_state and not new_state[i])
    
    def _process_analog(self, data):
        """Обработка аналоговых значений"""
        if len(data) >= 6:
            # Левый стик
            self.analog_state['lx'] = data[0]
            self.analog_state['ly'] = data[1]
            
            # Правый стик
            self.analog_state['rx'] = data[2]
            self.analog_state['ry'] = data[3]
            
            # Аналоговые триггеры
            self.analog_state['l2'] = data[4]
            self.analog_state['r2'] = data[5]
    
    def _polling_loop(self):
        """Цикл опроса контроллера"""
        print(f"[INFO] Запуск потока опроса ({self.polling_rate} Гц)")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Обновляем состояние
                if self.connected:
                    success = self._update_controller_state()
                    if not success and self.read_count > 100:
                        # Переподключение при потере связи
                        self.connected = self._check_connection()
                
                # Поддерживаем частоту опроса
                elapsed = time.time() - start_time
                sleep_time = max(0, self.polling_interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"[ERROR] Критическая ошибка в потоке опроса: {e}")
                time.sleep(0.1)
    
    def start_polling(self):
        """Запуск фонового опроса контроллера"""
        if not self.running:
            self.running = True
            self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
            self.polling_thread.start()
            print(f"[INFO] Опрос контроллера запущен")
    
    def stop_polling(self):
        """Остановка фонового опроса"""
        if self.running:
            self.running = False
            if self.polling_thread:
                self.polling_thread.join(timeout=1.0)
            print(f"[INFO] Опрос контроллера остановлен")
    
    # Методы для чтения состояния
    
    def is_pressed(self, button):
        """Проверка, нажата ли кнопка в данный момент"""
        if 0 <= button < 16:
            return self.button_state[button]
        return False
    
    def was_pressed(self, button):
        """Проверка, была ли кнопка только что нажата"""
        if 0 <= button < 16:
            return self.button_pressed[button]
        return False
    
    def was_released(self, button):
        """Проверка, была ли кнопка только что отпущена"""
        if 0 <= button < 16:
            return self.button_released[button]
        return False
    
    def get_analog(self, axis):
        """Получение аналогового значения"""
        return self.analog_state.get(axis, 128)
    
    def get_all_buttons(self):
        """Получение состояния всех кнопок"""
        return self.button_state.copy()
    
    def get_all_analog(self):
        """Получение всех аналоговых значений"""
        return self.analog_state.copy()
    
    def get_stats(self):
        """Получение статистики"""
        return {
            'read_count': self.read_count,
            'error_count': self.error_count,
            'success_rate': (self.read_count - self.error_count) / max(1, self.read_count) * 100,
            'connected': self.connected,
            'analog_mode': self.analog_mode,
            'polling_rate': self.polling_rate
        }
    
    def get_formatted_output(self, clear_screen=False):
        """Форматированный вывод состояния контроллера"""
        output = []
        
        # Заголовок
        output.append("=" * 50)
        output.append("PS2 CONTROLLER STATUS (gpiozero)")
        output.append("=" * 50)
        
        # Статистика
        stats = self.get_stats()
        output.append(f"Reads: {stats['read_count']} | "
                     f"Errors: {stats['error_count']} | "
                     f"Success: {stats['success_rate']:.1f}%")
        output.append(f"Connected: {self.connected} | "
                     f"Analog: {self.analog_mode} | "
                     f"Rate: {self.polling_rate}Hz")
        
        # Кнопки
        output.append("\n" + "-" * 50)
        output.append("BUTTONS (True = Pressed):")
        output.append("-" * 50)
        
        # Группируем кнопки для компактного вывода
        button_lines = []
        for i in range(0, 16, 4):
            line = []
            for j in range(4):
                idx = i + j
                if idx < 16:
                    name = self.BUTTON_NAMES[idx]
                    state = "✓" if self.button_state[idx] else " "
                    line.append(f"{name:10} [{state}]")
            button_lines.append("  ".join(line))
        
        output.extend(button_lines)
        
        # Аналоговые значения
        output.append("\n" + "-" * 50)
        output.append("ANALOG VALUES (0-255, 128=center):")
        output.append("-" * 50)
        
        # Стики
        output.append(f"Left Stick:  X={self.analog_state['lx']:3d}  Y={self.analog_state['ly']:3d}")
        output.append(f"Right Stick: X={self.analog_state['rx']:3d}  Y={self.analog_state['ry']:3d}")
        
        # Триггеры
        output.append(f"Triggers:    L2={self.analog_state['l2']:3d}  R2={self.analog_state['r2']:3d}")
        
        # Графическое представление стиков
        output.append("\n" + "-" * 50)
        output.append("STICK VISUALIZATION:")
        output.append("-" * 50)
        
        # Левый стик
        lx_norm = (self.analog_state['lx'] - 128) / 128
        ly_norm = (self.analog_state['ly'] - 128) / 128
        output.append(f"Left:  X:{'←' if lx_norm < -0.1 else '→' if lx_norm > 0.1 else '•'} "
                     f"Y:{'↑' if ly_norm < -0.1 else '↓' if ly_norm > 0.1 else '•'}")
        
        # Правый стик
        rx_norm = (self.analog_state['rx'] - 128) / 128
        ry_norm = (self.analog_state['ry'] - 128) / 128
        output.append(f"Right: X:{'←' if rx_norm < -0.1 else '→' if rx_norm > 0.1 else '•'} "
                     f"Y:{'↑' if ry_norm < -0.1 else '↓' if ry_norm > 0.1 else '•'}")
        
        output.append("=" * 50)
        
        # Сохраняем в очередь для плавного вывода
        self.output_queue.append("\n".join(output))
        
        return self.output_queue[-1]
    
    def cleanup(self):
        """Очистка ресурсов"""
        print("[INFO] Очистка ресурсов контроллера...")
        self.stop_polling()
        
        # Закрываем устройства gpiozero
        self.data.close()
        self.cmd.close()
        self.att.close()
        self.clk.close()
        
        print("[INFO] Ресурсы освобождены")