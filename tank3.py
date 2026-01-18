#!/usr/bin/env python3
"""
Управление гусеничным роботом с ПРЯМЫМ подключением PS2 к GPIO
Драйвер моторов: SZDoit (L298N)
Платформа: Raspberry Pi
"""

import time
import threading
import RPi.GPIO as GPIO
from enum import Enum
from typing import List, Optional
import os

# =================== НАСТРОЙКИ ===================
MIN_DUTY = 120        # мин. ШИМ для старта мотора (0-255)
DEAD_ZONE = 15        # мертвая зона стиков
MOTOR_MAX = 255       # максимальная скорость
PWM_FREQ = 1000       # частота ШИМ (Гц)

# =================== ПИНЫ GPIO ===================
# Пины драйвера SZDoit (BCM нумерация)
MOT_R_EN = 13         # GPIO13 - ENA правого мотора (ШИМ)
MOT_R_IN1 = 19        # GPIO19 - IN1 правого мотора
MOT_R_IN2 = 26        # GPIO26 - IN2 правого мотора

MOT_L_EN = 12         # GPIO12 - ENB левого мотора (ШИМ)
MOT_L_IN1 = 16        # GPIO16 - IN3 левого мотора
MOT_L_IN2 = 20        # GPIO20 - IN4 левого мотора

# Пины ПРЯМОГО подключения PS2 контроллера к GPIO
PS2_DAT = 27          # GPIO27 - DATA (фиолетовый)
PS2_CMD = 22          # GPIO22 - COMMAND (синий)
PS2_SEL = 23          # GPIO23 - ATTENTION/SELECT (зеленый)
PS2_CLK = 24          # GPIO24 - CLOCK (оранжевый)

# Светодиоды статуса
LED_PS2 = 21          # GPIO21 - светодиод подключения PS2
LED_MOTOR = 6         # GPIO6  - светодиод работы моторов

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)

# =================== КЛАСС ПРЯМОГО ПОДКЛЮЧЕНИЯ PS2 ===================
class DirectPS2Controller:
    """Класс для прямого подключения PS2 контроллера к GPIO Raspberry Pi"""
    
    def __init__(self):
        self.connected = False
        self.controller_type = "Unknown"
        self.analog_mode = False
        
        # Данные геймпада
        self.lx = 128
        self.ly = 128
        self.rx = 128
        self.ry = 128
        self.buttons = {
            'select': False, 'start': False,
            'up': False, 'down': False, 'left': False, 'right': False,
            'l1': False, 'r1': False, 'l2': False, 'r2': False,
            'triangle': False, 'circle': False, 'cross': False, 'square': False,
            'l3': False, 'r3': False
        }
        
        # Настройка пинов PS2
        self.setup_ps2_pins()
        
        # Инициализация контроллера
        self.init_controller()
        
    def setup_ps2_pins(self):
        """Настройка пинов для подключения PS2 контроллера"""
        print("Настройка пинов PS2...")
        
        # DAT - вход с подтяжкой к питанию
        GPIO.setup(PS2_DAT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # CMD, SEL, CLK - выходы
        GPIO.setup(PS2_CMD, GPIO.OUT)
        GPIO.setup(PS2_SEL, GPIO.OUT)
        GPIO.setup(PS2_CLK, GPIO.OUT)
        
        # Установка начальных состояний
        GPIO.output(PS2_SEL, GPIO.HIGH)  # Неактивный уровень
        GPIO.output(PS2_CLK, GPIO.HIGH)  # Неактивный уровень
        GPIO.output(PS2_CMD, GPIO.HIGH)  # Неактивный уровень
        
    def init_controller(self):
        """Инициализация PS2 контроллера"""
        print("Инициализация PS2 контроллера...")
        
        # Даем время на стабилизацию питания
        time.sleep(0.5)
        
        # Пробуем обратиться к контроллеру
        response = self.send_command(0x01)  # Команда инициализации
        
        if response and response[0] != 0xFF:
            self.connected = True
            controller_id = response[1]
            
            # Определение типа контроллера
            controllers = {
                0x41: "Digital Controller",
                0x23: "DualShock (Digital)",
                0x73: "DualShock (Analog)",
                0x79: "DualShock 2",
            }
            
            self.controller_type = controllers.get(controller_id, f"Unknown (0x{controller_id:02X})")
            print(f"✓ PS2 контроллер подключен: {self.controller_type}")
            
            # Попытка включить аналоговый режим
            self.enable_analog_mode()
            
        else:
            print("✗ PS2 контроллер не отвечает")
            print("  Проверьте подключение:")
            print(f"  DAT(GPIO{PS2_DAT}) CMD(GPIO{PS2_CMD}) SEL(GPIO{PS2_SEL}) CLK(GPIO{PS2_CLK})")
            print("  VCC -> 3.3V, GND -> земля")
            
    def send_byte(self, data: int) -> int:
        """Отправка одного байта и чтение ответа"""
        received = 0
        
        for i in range(8):
            # Опускаем CLK
            GPIO.output(PS2_CLK, GPIO.LOW)
            time.sleep(0.00001)  # 10 мкс
            
            # Устанавливаем бит на CMD
            bit_to_send = (data >> i) & 0x01
            GPIO.output(PS2_CMD, GPIO.HIGH if bit_to_send else GPIO.LOW)
            time.sleep(0.00001)
            
            # Поднимаем CLK
            GPIO.output(PS2_CLK, GPIO.HIGH)
            time.sleep(0.00001)
            
            # Читаем бит с DAT
            bit_received = GPIO.input(PS2_DAT)
            received |= (bit_received << i)
            
            time.sleep(0.00001)
            
        return received
    
    def send_command(self, command: int, read_bytes: int = 6) -> Optional[List[int]]:
        """Отправка команды PS2 контроллеру"""
        response = []
        
        try:
            # Активируем линию SEL (ATTENTION)
            GPIO.output(PS2_SEL, GPIO.LOW)
            time.sleep(0.0001)  # 100 мкс
            
            # Отправляем команду и читаем первый байт
            first_byte = self.send_byte(command)
            response.append(first_byte)
            
            # Читаем дополнительные байты
            for _ in range(read_bytes):
                response.append(self.send_byte(0x00))
            
            # Деактивируем SEL
            GPIO.output(PS2_SEL, GPIO.HIGH)
            time.sleep(0.0001)
            
            return response
            
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")
            GPIO.output(PS2_SEL, GPIO.HIGH)
            return None
    
    def enable_analog_mode(self):
        """Включение аналогового режима (для DualShock)"""
        if "DualShock" in self.controller_type:
            print("Включение аналогового режима...")
            response = self.send_command(0x44)  # Команда включения аналога
            
            if response and response[1] == 0x73:
                # Подтверждаем режим
                self.send_command(0x4F)
                self.analog_mode = True
                print("✓ Аналоговый режим включен")
    
    def read(self):
        """Чтение текущего состояния контроллера"""
        if not self.connected:
            return
            
        # Команда чтения состояния контроллера (0x42)
        response = self.send_command(0x42, 8)
        
        if not response or response[0] == 0xFF:
            self.connected = False
            return
            
        # Разбор данных кнопок (первые 2 байта)
        btn1 = response[1]
        btn2 = response[2]
        
        # Обновление состояния кнопок
        self.buttons['select'] = not (btn1 & 0x01)
        self.buttons['l3'] = not (btn1 & 0x02)
        self.buttons['r3'] = not (btn1 & 0x04)
        self.buttons['start'] = not (btn1 & 0x08)
        self.buttons['up'] = not (btn1 & 0x10)
        self.buttons['right'] = not (btn1 & 0x20)
        self.buttons['down'] = not (btn1 & 0x40)
        self.buttons['left'] = not (btn1 & 0x80)
        
        self.buttons['l2'] = not (btn2 & 0x01)
        self.buttons['r2'] = not (btn2 & 0x02)
        self.buttons['l1'] = not (btn2 & 0x04)
        self.buttons['r1'] = not (btn2 & 0x08)
        self.buttons['triangle'] = not (btn2 & 0x10)
        self.buttons['circle'] = not (btn2 & 0x20)
        self.buttons['cross'] = not (btn2 & 0x40)
        self.buttons['square'] = not (btn2 & 0x80)
        
        # Чтение аналоговых стиков
        if len(response) >= 9:
            self.lx = response[3]  # Левый стик X
            self.ly = response[4]  # Левый стик Y
            self.rx = response[5]  # Правый стик X
            self.ry = response[6]  # Правый стик Y
            
            # Аналоговые триггеры L2/R2 (если есть)
            if len(response) >= 11:
                self.buttons['l2_value'] = response[9]
                self.buttons['r2_value'] = response[10]
    
    def analog(self, stick: str) -> int:
        """Получение значения аналогового стика"""
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
        GPIO.output(PS2_SEL, GPIO.HIGH)
        GPIO.output(PS2_CLK, GPIO.HIGH)
        GPIO.output(PS2_CMD, GPIO.HIGH)

# =================== КЛАСС МОТОРА SZDoit ===================
class SZDoitMotor:
    """Класс для управления мотором через драйвер SZDoit"""
    
    def __init__(self, en_pin: int, in1_pin: int, in2_pin: int, 
                 name: str = "Motor", reverse: bool = False):
        self.name = name
        self.reverse = reverse
        self.en_pin = en_pin
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        
        # Настройка пинов
        GPIO.setup(en_pin, GPIO.OUT)
        GPIO.setup(in1_pin, GPIO.OUT)
        GPIO.setup(in2_pin, GPIO.OUT)
        
        # Создание ШИМ объекта
        self.pwm = GPIO.PWM(en_pin, PWM_FREQ)
        self.pwm.start(0)
        
        # Переменные состояния
        self.target_speed = 0
        self.current_speed = 0
        self.smooth_factor = 80
        self.min_duty = MIN_DUTY
        
        # Начальное состояние - остановка
        self._set_direction(0)
        
    def set_speed(self, speed: int):
        """Установка целевой скорости (-255..255)"""
        self.target_speed = max(-MOTOR_MAX, min(MOTOR_MAX, speed))
        
    def smooth_update(self):
        """Плавное обновление скорости"""
        if abs(self.target_speed - self.current_speed) > 0.5:
            diff = self.target_speed - self.current_speed
            self.current_speed += diff * (self.smooth_factor / 100.0)
        else:
            self.current_speed = self.target_speed
            
        self._apply_speed()
        
    def _apply_speed(self):
        """Применение текущей скорости к мотору"""
        speed = self.current_speed
        
        if self.reverse:
            speed = -speed
            
        # Учет минимального сигнала
        if abs(speed) > 0 and abs(speed) < self.min_duty:
            speed = self.min_duty if speed > 0 else -MIN_DUTY
            
        # Установка направления и ШИМ
        if speed > 0:
            self._set_direction(1)
            duty = (speed / MOTOR_MAX) * 100
            self.pwm.ChangeDutyCycle(duty)
        elif speed < 0:
            self._set_direction(-1)
            duty = (-speed / MOTOR_MAX) * 100
            self.pwm.ChangeDutyCycle(duty)
        else:
            self._set_direction(0)
            self.pwm.ChangeDutyCycle(0)
            
    def _set_direction(self, direction: int):
        """Установка направления вращения"""
        if direction == 1:
            GPIO.output(self.in1_pin, GPIO.HIGH)
            GPIO.output(self.in2_pin, GPIO.LOW)
        elif direction == -1:
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.HIGH)
        else:
            GPIO.output(self.in1_pin, GPIO.LOW)
            GPIO.output(self.in2_pin, GPIO.LOW)
            
    def stop(self):
        """Мгновенная остановка"""
        self.target_speed = 0
        self.current_speed = 0
        self.pwm.ChangeDutyCycle(0)
        self._set_direction(0)
        
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop()
        self.pwm.stop()

# =================== ГЛАВНЫЙ КЛАСС УПРАВЛЕНИЯ ===================
class TankRobotController:
    """Основной класс управления гусеничным роботом с прямым PS2 подключением"""
    
    def __init__(self):
        self.print_header()
        
        # Настройка светодиодов
        GPIO.setup(LED_PS2, GPIO.OUT)
        GPIO.setup(LED_MOTOR, GPIO.OUT)
        GPIO.output(LED_PS2, GPIO.LOW)
        GPIO.output(LED_MOTOR, GPIO.LOW)
        
        # Инициализация моторов SZDoit
        print("\nИнициализация моторов SZDoit...")
        self.motorR = SZDoitMotor(MOT_R_EN, MOT_R_IN1, MOT_R_IN2, 
                                 "Правый мотор", reverse=True)
        self.motorL = SZDoitMotor(MOT_L_EN, MOT_L_IN1, MOT_L_IN2,
                                 "Левый мотор", reverse=False)
        
        # Настройка моторов
        self.motorR.set_smoothness(80)
        self.motorL.set_smoothness(80)
        self.motorR.set_min_duty(MIN_DUTY)
        self.motorL.set_min_duty(MIN_DUTY)
        print("✓ Моторы инициализированы")
        
        # Инициализация ПРЯМОГО PS2 подключения
        print("\nИнициализация прямого PS2 подключения...")
        self.ps2 = DirectPS2Controller()
        
        if self.ps2.connected:
            GPIO.output(LED_PS2, GPIO.HIGH)
        
        # Переменные состояния
        self.control_mode = 0  # 0=танковая схема, 1=машинная схема
        self.emergency_stop = False
        self.is_running = True
        self.last_status_time = time.time()
        
    def print_header(self):
        """Вывод информации о подключении"""
        print("=" * 70)
        print("ГУСЕНИЧНЫЙ РОБОТ - ПРЯМОЕ ПОДКЛЮЧЕНИЕ PS2 К GPIO")
        print("=" * 70)
        
        print("\n=== СХЕМА ПОДКЛЮЧЕНИЯ ===")
        
        print("\nДрайвер SZDoit:")
        print(f"  Правый мотор: ENA=GPIO{MOT_R_EN}({self.gpio_to_physical(MOT_R_EN)}), "
              f"IN1=GPIO{MOT_R_IN1}({self.gpio_to_physical(MOT_R_IN1)}), "
              f"IN2=GPIO{MOT_R_IN2}({self.gpio_to_physical(MOT_R_IN2)})")
        print(f"  Левый мотор:  ENB=GPIO{MOT_L_EN}({self.gpio_to_physical(MOT_L_EN)}), "
              f"IN3=GPIO{MOT_L_IN1}({self.gpio_to_physical(MOT_L_IN1)}), "
              f"IN4=GPIO{MOT_L_IN2}({self.gpio_to_physical(MOT_L_IN2)})")
        
        print("\nPS2 контроллер (прямое подключение):")
        print(f"  DAT=GPIO{PS2_DAT}({self.gpio_to_physical(PS2_DAT)}) - фиолетовый")
        print(f"  CMD=GPIO{PS2_CMD}({self.gpio_to_physical(PS2_CMD)}) - синий")
        print(f"  SEL=GPIO{PS2_SEL}({self.gpio_to_physical(PS2_SEL)}) - зеленый")
        print(f"  CLK=GPIO{PS2_CLK}({self.gpio_to_physical(PS2_CLK)}) - оранжевый")
        print(f"  VCC -> 3.3V (пин 1 или 17)")
        print(f"  GND -> GND (пин 6, 9, 14, 20, 25)")
        
        print("\nСветодиоды:")
        print(f"  PS2:   GPIO{LED_PS2}({self.gpio_to_physical(LED_PS2)})")
        print(f"  Мотор: GPIO{LED_MOTOR}({self.gpio_to_physical(LED_MOTOR)})")
        
        print("\n=== УПРАВЛЕНИЕ ===")
        print("Левый стик - движение")
        print("L1 - танковая схема")
        print("R1 - машинная схема")
        print("SELECT - экстренная остановка")
        print("START - снятие остановки")
        print("Ctrl+C - выход")
        print("=" * 70 + "\n")
        
    def gpio_to_physical(self, gpio_pin: int) -> int:
        """Конвертация GPIO в физический номер пина"""
        gpio_to_physical_map = {
            6: 31, 12: 32, 13: 33, 16: 36,
            19: 35, 20: 38, 21: 40, 22: 15,
            23: 16, 24: 18, 26: 37, 27: 13,
        }
        return gpio_to_physical_map.get(gpio_pin, 0)
        
    def map_value(self, x: int, in_min: int, in_max: int, 
                  out_min: int, out_max: int) -> int:
        """Преобразование значения"""
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
        
    def process_controls(self):
        """Обработка управления с PS2 контроллера"""
        # Чтение данных с PS2
        self.ps2.read()
        
        if not self.ps2.connected:
            # Мигание светодиодом при отсутствии подключения
            if int(time.time() * 2) % 2 == 0:
                GPIO.output(LED_PS2, GPIO.HIGH)
            else:
                GPIO.output(LED_PS2, GPIO.LOW)
            return
            
        # Экстренная остановка
        if self.ps2.button('select'):
            if not self.emergency_stop:
                self.emergency_stop = True
                self.motorR.stop()
                self.motorL.stop()
                print("\n!!! ЭКСТРЕННАЯ ОСТАНОВКА !!!")
                GPIO.output(LED_MOTOR, GPIO.LOW)
                GPIO.output(LED_PS2, GPIO.LOW)
                time.sleep(0.5)
                GPIO.output(LED_PS2, GPIO.HIGH)
            return
            
        # Снятие экстренной остановки
        if self.emergency_stop and self.ps2.button('start'):
            self.emergency_stop = False
            print("\n✓ Снята экстренная остановка")
            GPIO.output(LED_PS2, GPIO.HIGH)
            
        # Если активна экстренная остановка
        if self.emergency_stop:
            return
            
        # Смена режима управления
        if self.ps2.button('l1'):
            self.control_mode = 0
            print("\n✓ Режим: ТАНКОВАЯ СХЕМА")
            time.sleep(0.3)
            
        if self.ps2.button('r1'):
            self.control_mode = 1
            print("\n✓ Режим: МАШИННАЯ СХЕМА")
            time.sleep(0.3)
            
        # Получение значений стиков
        lx_raw = self.ps2.analog('LX')
        ly_raw = self.ps2.analog('LY')
        
        # Преобразование 0..255 в -255..255
        LX = self.map_value(lx_raw, 0, 255, -255, 255)
        LY = self.map_value(ly_raw, 0, 255, -255, 255)
        
        # Применение мертвой зоны
        if abs(LX) < DEAD_ZONE:
            LX = 0
        if abs(LY) < DEAD_ZONE:
            LY = 0
            
        # Вычисление скоростей моторов
        if self.control_mode == 0:
            # Танковая схема
            speedR = LY + LX
            speedL = LY - LX
        else:
            # Машинная схема
            speedR = LY + LX * 0.7
            speedL = LY - LX * 0.7
            
        # Ограничение скоростей
        speedR = max(-255, min(255, int(speedR)))
        speedL = max(-255, min(255, int(speedL)))
        
        # Установка скоростей
        self.motorR.set_speed(speedR)
        self.motorL.set_speed(speedL)
        
        # Управление светодиодами
        if speedR != 0 or speedL != 0:
            GPIO.output(LED_MOTOR, GPIO.HIGH)
        else:
            GPIO.output(LED_MOTOR, GPIO.LOW)
            
        # Вывод статуса раз в секунду
        current_time = time.time()
        if current_time - self.last_status_time > 1.0:
            self.last_status_time = current_time
            mode = "ТАНК" if self.control_mode == 0 else "МАШИНА"
            lx_display = LX if abs(LX) >= DEAD_ZONE else 0
            ly_display = LY if abs(LY) >= DEAD_ZONE else 0
            print(f"\rLX:{lx_display:+4d} LY:{ly_display:+4d} | "
                  f"R:{speedR:+4d} L:{speedL:+4d} | {mode}", end="", flush=True)
            
    def run(self):
        """Основной цикл работы"""
        print("Запуск основного цикла управления...")
        
        try:
            while self.is_running:
                # Обработка управления
                self.process_controls()
                
                # Плавное обновление моторов
                self.motorR.smooth_update()
                self.motorL.smooth_update()
                
                # Задержка для стабильной работы (50 Гц)
                time.sleep(0.02)
                
        except KeyboardInterrupt:
            print("\n\nПолучен сигнал прерывания")
            
        finally:
            self.shutdown()
            
    def shutdown(self):
        """Корректное завершение работы"""
        print("\nЗавершение работы...")
        
        # Остановка моторов
        print("Остановка моторов...")
        self.motorR.stop()
        self.motorL.stop()
        
        # Очистка ресурсов
        print("Очистка ресурсов...")
        self.motorR.cleanup()
        self.motorL.cleanup()
        self.ps2.cleanup()
        GPIO.cleanup()
        
        print("✓ Все ресурсы освобождены")

# =================== ПРОВЕРКА И ЗАПУСК ===================
if __name__ == "__main__":
    # Проверка запуска от root
    if os.geteuid() != 0:
        print("ОШИБКА: Запустите программу с sudo!")
        print("  sudo python3 direct_ps2_robot.py")
        exit(1)
        
    # Запуск контроллера
    try:
        controller = TankRobotController()
        controller.run()
    except Exception as e:
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}")
        GPIO.cleanup()