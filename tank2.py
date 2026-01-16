#!/usr/bin/env python3
"""
Управление гусеничным роботом с PS2 геймпадом на Raspberry Pi 4
Требуется: pip3 install rpi.gpio pygame
"""

import time
import math
import threading
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
import RPi.GPIO as GPIO
import pygame  # для эмуляции геймпада или работы с реальным через USB

# =================== КОНСТАНТЫ ===================
MIN_DUTY = 120  # мин. сигнал, при котором мотор начинает вращение

# Пины драйвера (используем BCM нумерацию)
MOT_RA = 2   # GPIO2
MOT_RB = 3   # GPIO3
MOT_LA = 4   # GPIO4
MOT_LB = 17  # GPIO17

# Пины для реального PS2 контроллера (если подключен напрямую к GPIO)
PS2_DAT = 27  # GPIO27
PS2_CMD = 22  # GPIO22
PS2_SEL = 23  # GPIO23
PS2_CLK = 24  # GPIO24

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# =================== КЛАСС МОТОРА С ШИМ ===================
class GMotor:
    def __init__(self, pinA: int, pinB: int, name: str = "Motor", reverse: bool = False, frequency: int = 1000):
        self.name = name
        self.reverse = reverse
        self.pinA = pinA
        self.pinB = pinB
        
        # Настройка пинов как выходов с ШИМ
        GPIO.setup(pinA, GPIO.OUT)
        GPIO.setup(pinB, GPIO.OUT)
        
        # Создаем ШИМ объекты
        self.pwmA = GPIO.PWM(pinA, frequency)
        self.pwmB = GPIO.PWM(pinB, frequency)
        
        # Запускаем ШИМ с 0% заполнением
        self.pwmA.start(0)
        self.pwmB.start(0)
        
        self.target_speed = 0
        self.current_speed = 0
        self.smooth_factor = 80  # 0-100, чем больше - тем плавнее
        self.min_duty = MIN_DUTY
        self.last_update = time.time()
        
    def set_speed(self, speed: int):
        """Установка скорости (-255..255)"""
        self.target_speed = max(-255, min(255, speed))
        
    def smooth_tick(self):
        """Плавное изменение скорости"""
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Интерполяция для плавности (50 Гц эквивалент)
        if abs(self.target_speed - self.current_speed) > 0.5:
            diff = self.target_speed - self.current_speed
            smooth_step = (self.smooth_factor / 100.0) * (dt * 50.0)
            self.current_speed += diff * smooth_step
        else:
            self.current_speed = self.target_speed
            
        self._apply_speed()
    
    def _apply_speed(self):
        """Применение скорости к моторам через ШИМ"""
        speed = self.current_speed
        
        if self.reverse:
            speed = -speed
            
        # Учет минимального сигнала
        if abs(speed) > 0 and abs(speed) < self.min_duty:
            speed = self.min_duty if speed > 0 else -self.min_duty
            
        # Преобразуем -255..255 в 0..100 для ШИМ
        duty = abs(speed) * 100.0 / 255.0
        
        if speed > 0:
            # Вперед
            self.pwmA.ChangeDutyCycle(duty)
            self.pwmB.ChangeDutyCycle(0)
        elif speed < 0:
            # Назад
            self.pwmA.ChangeDutyCycle(0)
            self.pwmB.ChangeDutyCycle(duty)
        else:
            # Стоп
            self.pwmA.ChangeDutyCycle(0)
            self.pwmB.ChangeDutyCycle(0)
    
    def set_smoothness(self, factor: int):
        """Установка плавности (0-100)"""
        self.smooth_factor = max(0, min(100, factor))
        
    def set_min_duty(self, duty: int):
        """Установка минимального сигнала"""
        self.min_duty = duty
        
    def stop(self):
        """Мгновенная остановка"""
        self.target_speed = 0
        self.current_speed = 0
        self.pwmA.ChangeDutyCycle(0)
        self.pwmB.ChangeDutyCycle(0)
        
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop()
        self.pwmA.stop()
        self.pwmB.stop()
        
    def __str__(self) -> str:
        return f"{self.name}: {self.current_speed:+4d} (target: {self.target_speed:+4d})"

# =================== КЛАСС PS2 КОНТРОЛЛЕРА ===================
class PS2XController:
    def __init__(self, use_pygame: bool = True, use_gpio: bool = False):
        """
        Инициализация PS2 контроллера
        
        Args:
            use_pygame: Использовать pygame для USB геймпада
            use_gpio: Использовать прямое подключение к GPIO (требуется специальная библиотека)
        """
        self.use_pygame = use_pygame
        self.use_gpio = use_gpio
        self.connected = False
        
        # Данные геймпада
        self.lx = 128  # 0-255, 128 = центр
        self.ly = 128
        self.rx = 128
        self.ry = 128
        self.buttons = {
            'select': False,
            'start': False,
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'l1': False,
            'r1': False,
            'l2': False,
            'r2': False,
            'triangle': False,
            'circle': False,
            'cross': False,
            'square': False,
            'l3': False,
            'r3': False
        }
        
        if use_pygame:
            self._init_pygame()
        elif use_gpio:
            self._init_gpio()
            
    def _init_pygame(self):
        """Инициализация pygame для USB геймпада"""
        try:
            pygame.init()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.connected = True
                print(f"✓ Подключен геймпад: {self.joystick.get_name()}")
                print(f"  Оси: {self.joystick.get_numaxes()}, Кнопки: {self.joystick.get_numbuttons()}")
            else:
                print("⚠ Геймпад не найден. Используем клавиатуру (WASD + Q/E для режимов).")
                self.joystick = None
                self.connected = True  # Все равно можно управлять с клавиатуры
        except Exception as e:
            print(f"✗ Ошибка инициализации pygame: {e}")
            self.connected = False
            
    def _init_gpio(self):
        """Инициализация PS2 контроллера на GPIO (упрощенная версия)"""
        try:
            # Настройка пинов для протокола SPI-like
            GPIO.setup(PS2_DAT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(PS2_CMD, GPIO.OUT)
            GPIO.setup(PS2_SEL, GPIO.OUT)
            GPIO.setup(PS2_CLK, GPIO.OUT)
            
            GPIO.output(PS2_SEL, GPIO.HIGH)
            GPIO.output(PS2_CLK, GPIO.HIGH)
            GPIO.output(PS2_CMD, GPIO.HIGH)
            
            self.connected = True
            print("✓ PS2 контроллер инициализирован на GPIO")
        except Exception as e:
            print(f"✗ Ошибка инициализации GPIO для PS2: {e}")
            self.connected = False
            
    def read(self):
        """Чтение данных с геймпада"""
        if self.use_pygame:
            self._read_pygame()
        elif self.use_gpio:
            self._read_gpio()
            
    def _read_pygame(self):
        """Чтение данных через pygame"""
        if not self.connected:
            return
            
        pygame.event.pump()
        
        if self.joystick:
            try:
                # Чтение аналоговых стиков
                # Обычно оси 0,1 - левый стик, 2,3 - правый стик
                axes_count = self.joystick.get_numaxes()
                
                if axes_count >= 2:
                    self.lx = int((self.joystick.get_axis(0) + 1) * 127.5)  # -1..1 to 0..255
                    self.ly = int((self.joystick.get_axis(1) + 1) * 127.5)
                
                if axes_count >= 4:
                    self.rx = int((self.joystick.get_axis(2) + 1) * 127.5)
                    self.ry = int((self.joystick.get_axis(3) + 1) * 127.5)
                
                # Чтение кнопок
                buttons_count = self.joystick.get_numbuttons()
                
                # Маппинг кнопок для PlayStation контроллера
                button_map = {
                    0: 'cross',     # X
                    1: 'circle',    # O
                    2: 'triangle',  # △
                    3: 'square',    # □
                    4: 'l1',
                    5: 'r1',
                    6: 'l2',
                    7: 'r2',
                    8: 'select',
                    9: 'start',
                    10: 'l3',
                    11: 'r3'
                }
                
                for btn_num, btn_name in button_map.items():
                    if btn_num < buttons_count:
                        self.buttons[btn_name] = self.joystick.get_button(btn_num)
                
                # Чтение D-pad (крестовины)
                if self.joystick.get_numhats() > 0:
                    hat = self.joystick.get_hat(0)
                    self.buttons['left'] = hat[0] == -1
                    self.buttons['right'] = hat[0] == 1
                    self.buttons['up'] = hat[1] == 1
                    self.buttons['down'] = hat[1] == -1
                    
            except Exception as e:
                print(f"⚠ Ошибка чтения геймпада: {e}")
                self.connected = False
        else:
            # Управление с клавиатуры
            keys = pygame.key.get_pressed()
            
            # WASD для левого стика
            self.ly = 128
            self.lx = 128
            
            if keys[pygame.K_w]:
                self.ly = 0  # Вперед
            elif keys[pygame.K_s]:
                self.ly = 255  # Назад
                
            if keys[pygame.K_a]:
                self.lx = 0  # Влево
            elif keys[pygame.K_d]:
                self.lx = 255  # Вправо
                
            # Кнопки на клавиатуре
            self.buttons['select'] = keys[pygame.K_BACKSPACE]
            self.buttons['r1'] = keys[pygame.K_e]  # Смена режима
            self.buttons['l1'] = keys[pygame.K_q]  # Смена режима
            self.buttons['start'] = keys[pygame.K_RETURN]
            
    def _read_gpio(self):
        """Чтение данных с PS2 контроллера через GPIO (упрощенная реализация)"""
        # Эта функция требует реализации протокола PS2
        # Здесь упрощенная версия для демонстрации
        pass
        
    def analog(self, stick: str) -> int:
        """Получение значения аналогового стика (0-255)"""
        if stick == 'LX':
            return self.lx
        elif stick == 'LY':
            return self.ly
        elif stick == 'RX':
            return self.rx
        elif stick == 'RY':
            return self.ry
        return 128
        
    def button(self, btn: str) -> bool:
        """Проверка нажатия кнопки"""
        return self.buttons.get(btn, False)
        
    def cleanup(self):
        """Очистка ресурсов"""
        if self.use_pygame:
            pygame.quit()

# =================== ОСНОВНОЙ КЛАСС УПРАВЛЕНИЯ ===================
class TankController:
    def __init__(self, use_real_ps2: bool = False):
        print("=" * 50)
        print("Инициализация гусеничного робота на Raspberry Pi 4")
        print("=" * 50)
        
        # Инициализация моторов
        print("\nИнициализация моторов...")
        self.motorR = GMotor(MOT_RA, MOT_RB, "Правый мотор", reverse=True)
        self.motorL = GMotor(MOT_LA, MOT_LB, "Левый мотор", reverse=False)
        
        # Настройка моторов
        self.motorR.set_smoothness(80)
        self.motorL.set_smoothness(80)
        self.motorR.set_min_duty(MIN_DUTY)
        self.motorL.set_min_duty(MIN_DUTY)
        
        print("✓ Моторы инициализированы")
        
        # Инициализация контроллера
        print("\nИнициализация контроллера PS2...")
        self.ps2 = PS2XController(use_pygame=True, use_gpio=use_real_ps2)
        
        if not self.ps2.connected:
            print("⚠ Контроллер не подключен. Используется клавиатура.")
        
        # Переменные управления
        self.control_mode = 0  # 0 - танковая схема, 1 - машинная
        self.is_running = True
        self.last_control_time = time.time()
        self.connection_errors = 0
        self.max_errors = 10
        
        # Флаг для экстренной остановки
        self.emergency_stop = False
        
        print("\n✓ Система готова к работе")
        print("\nУправление:")
        print("  Левый стик/WSAD - движение")
        print("  L1/Q - танковая схема")
        print("  R1/E - машинная схема")
        print("  SELECT - экстренная остановка")
        print("  CTRL+C - выход из программы")
        print("=" * 50)
        
    def map_value(self, x: int, in_min: int, in_max: int, out_min: int, out_max: int) -> int:
        """Аналог функции map из Arduino"""
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
        
    def constrain(self, value: int, min_val: int, max_val: int) -> int:
        """Ограничение значения"""
        return max(min_val, min(max_val, value))
        
    def process_controls(self):
        """Обработка управления с геймпада"""
        # Чтение геймпада
        self.ps2.read()
        
        if not self.ps2.connected:
            self.connection_errors += 1
            if self.connection_errors >= self.max_errors:
                print("⚠ Потеря связи с контроллером, остановка")
                self.motorR.set_speed(0)
                self.motorL.set_speed(0)
                return
        else:
            self.connection_errors = 0
            
        # Проверка экстренной остановки
        if self.ps2.button('select'):
            print("⚠ ЭКСТРЕННАЯ ОСТАНОВКА!")
            self.emergency_stop = True
            self.motorR.stop()
            self.motorL.stop()
            
            # Ждем отпускания кнопки
            while self.ps2.button('select'):
                self.ps2.read()
                time.sleep(0.01)
                
            self.emergency_stop = False
            print("✓ Снята экстренная остановка")
            return
            
        # Смена режима управления
        if self.ps2.button('l1'):
            self.control_mode = 0  # Танковая схема
            print("✓ Режим: ТАНКОВАЯ СХЕМА")
            time.sleep(0.3)  # Защита от двойного срабатывания
            
        if self.ps2.button('r1'):
            self.control_mode = 1  # Машинная схема
            print("✓ Режим: МАШИННАЯ СХЕМА")
            time.sleep(0.3)
            
        # Получаем значения стиков
        lx_raw = self.ps2.analog('LX')
        ly_raw = self.ps2.analog('LY')
        
        # Преобразуем 0..255 в -255..255
        LX = self.map_value(lx_raw, 255, 0, -255, 255)
        LY = self.map_value(ly_raw, 255, 0, -255, 255)
        
        # Мертвая зона для устранения дрейфа
        DEAD_ZONE = 15
        if abs(LX) < DEAD_ZONE:
            LX = 0
        if abs(LY) < DEAD_ZONE:
            LY = 0
            
        # Вычисление скоростей моторов
        if self.control_mode == 0:
            # Танковая схема
            dutyR = LY + LX
            dutyL = LY - LX
        else:
            # Машинная схема (дифференциальный привод)
            dutyR = LY + LX * 0.5
            dutyL = LY - LX * 0.5
            
        # Ограничение значений
        dutyR = self.constrain(int(dutyR), -255, 255)
        dutyL = self.constrain(int(dutyL), -255, 255)
        
        # Установка скоростей
        self.motorR.set_speed(dutyR)
        self.motorL.set_speed(dutyL)
        
    def display_status(self):
        """Отображение статуса системы"""
        print(f"\rМоторы: {self.motorL} | {self.motorR} | Режим: {'ТАНК' if self.control_mode == 0 else 'МАШИНА'}",
              end='', flush=True)
        
    def run(self):
        """Основной цикл работы"""
        print("\nЗапуск основного цикла...")
        
        try:
            while self.is_running:
                # Обработка управления
                self.process_controls()
                
                # Плавное обновление моторов
                self.motorR.smooth_tick()
                self.motorL.smooth_tick()
                
                # Отображение статуса
                self.display_status()
                
                # Задержка для стабильной работы (50 Гц)
                time.sleep(0.02)
                
        except KeyboardInterrupt:
            print("\n\n⚠ Получен сигнал прерывания (Ctrl+C)")
            
        finally:
            self.shutdown()
            
    def shutdown(self):
        """Корректное завершение работы"""
        print("\n\nЗавершение работы...")
        
        # Остановка моторов
        print("Остановка моторов...")
        self.motorR.stop()
        self.motorL.stop()
        time.sleep(0.1)
        
        # Очистка ресурсов
        print("Очистка ресурсов...")
        self.motorR.cleanup()
        self.motorL.cleanup()
        self.ps2.cleanup()
        GPIO.cleanup()
        
        print("✓ Все ресурсы освобождены")
        print("✓ Программа завершена")

# =================== ТОЧКА ВХОДА ===================
if __name__ == "__main__":
    print("Гусеничный робот на Raspberry Pi 4")
    print("Выберите тип подключения:")
    print("  1. USB геймпад (рекомендуется)")
    print("  2. PS2 контроллер на GPIO (экспериментально)")
    
    choice = input("Ваш выбор (1/2): ").strip()
    
    if choice == "2":
        use_real_ps2 = True
        print("Внимание: Режим PS2 на GPIO требует специальной проводки!")
    else:
        use_real_ps2 = False
        
    # Создание и запуск контроллера
    controller = TankController(use_real_ps2=use_real_ps2)
    
    # Запуск основного цикла
    controller.run()