#!/usr/bin/env python3
"""
ПРОСТОЙ ТЕСТ ПОДКЛЮЧЕНИЯ PS2 ГЕЙМПАДА
На Raspberry Pi через GPIO
"""

import RPi.GPIO as GPIO
import time

# Настройка пинов (физическая нумерация)
DAT = 13  # Фиолетовый провод (GPIO27)
CMD = 15  # Синий провод (GPIO22)
SEL = 16  # Зеленый провод (GPIO23)
CLK = 18  # Оранжевый провод (GPIO24)

def setup():
    """Настройка пинов"""
    GPIO.setmode(GPIO.BOARD)  # Используем номера на разъеме
    GPIO.setwarnings(True)
    
    # Настройка пинов
    GPIO.setup(DAT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(CMD, GPIO.OUT)
    GPIO.setup(SEL, GPIO.OUT)
    GPIO.setup(CLK, GPIO.OUT)
    
    # Установка начального состояния
    GPIO.output(SEL, GPIO.HIGH)
    GPIO.output(CLK, GPIO.HIGH)
    GPIO.output(CMD, GPIO.HIGH)

def send_byte(data):
    """Отправить один байт в контроллер"""
    received = 0
    
    for i in range(8):
        # Опускаем CLK
        GPIO.output(CLK, GPIO.LOW)
        time.sleep(0.00001)
        
        # Устанавливаем бит на CMD
        bit = (data >> i) & 1
        GPIO.output(CMD, GPIO.HIGH if bit else GPIO.LOW)
        time.sleep(0.00001)
        
        # Поднимаем CLK
        GPIO.output(CLK, GPIO.HIGH)
        time.sleep(0.00001)
        
        # Читаем бит с DAT
        received_bit = GPIO.input(DAT)
        received |= (received_bit << i)
        
        time.sleep(0.00001)
    
    return received

def test_controller():
    """Основной тест контроллера"""
    print("\n" + "="*50)
    print("ТЕСТ PS2 ГЕЙМПАДА НА RASPBERRY PI")
    print("="*50)
    
    print("\nПРОВЕРКА ПОДКЛЮЧЕНИЯ...")
    
    # Проверяем аппаратную часть
    print("1. Проверка линий GPIO...")
    try:
        GPIO.output(CLK, GPIO.LOW)
        time.sleep(0.001)
        GPIO.output(CLK, GPIO.HIGH)
        print("   ✓ CLK работает")
    except:
        print("   ✗ Ошибка CLK")
        return False
    
    # Пробуем обратиться к контроллеру
    print("\n2. Обращение к контроллеру...")
    
    try:
        # Активируем контроллер
        GPIO.output(SEL, GPIO.LOW)
        time.sleep(0.0001)
        
        # Отправляем команду "Привет" (0x01)
        print("   Отправляю команду 0x01...")
        response1 = send_byte(0x01)
        print(f"   Ответ: {hex(response1)}")
        
        # Читаем еще 5 байтов
        responses = [response1]
        for i in range(5):
            resp = send_byte(0x00)
            responses.append(resp)
        
        # Деактивируем контроллер
        GPIO.output(SEL, GPIO.HIGH)
        
        print(f"   Все ответы: {[hex(x) for x in responses]}")
        
        # Анализируем ответ
        if responses[0] == 0xFF:
            print("\n   ✗ Контроллер не ответил (получен 0xFF)")
            print("   Проверьте:")
            print("   - Подключен ли контроллер")
            print("   - Включен ли он (красный светодиод)")
            print("   - Нажата ли кнопка Analog/Mode")
            return False
        else:
            print(f"\n   ✓ Контроллер ответил! ID: {hex(responses[1])}")
            
            # Определяем тип контроллера
            controller_id = responses[1]
            if controller_id == 0x41:
                print("   Тип: Цифровой контроллер PlayStation")
            elif controller_id == 0x73:
                print("   Тип: Аналоговый контроллер (DualShock)")
            elif controller_id == 0x79:
                print("   Тип: DualShock 2")
            else:
                print(f"   Тип: Неизвестный (ID: {hex(controller_id)})")
            
            return True
            
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        GPIO.output(SEL, GPIO.HIGH)
        return False

def read_buttons():
    """Чтение кнопок в реальном времени"""
    print("\n3. ТЕСТ КНОПОК И СТИКОВ")
    print("   Нажимайте кнопки, двигайте стики...")
    print("   Для выхода нажмите Ctrl+C\n")
    
    try:
        count = 0
        while True:
            # Команда чтения состояния (0x42)
            GPIO.output(SEL, GPIO.LOW)
            time.sleep(0.0001)
            
            # Отправляем команду и читаем ответ
            responses = []
            responses.append(send_byte(0x42))  # Команда
            
            for i in range(8):  # Читаем 8 байтов данных
                responses.append(send_byte(0x00))
            
            GPIO.output(SEL, GPIO.HIGH)
            
            # Выводим состояние каждые 10 раз
            count += 1
            if count % 10 == 0:
                print(f"\n--- ОПРОС #{count} ---")
                
                # Байты 1-2: кнопки
                btn1 = responses[1]
                btn2 = responses[2]
                
                # Проверяем основные кнопки
                buttons = []
                if not (btn1 & 0x01): buttons.append("SELECT")
                if not (btn1 & 0x08): buttons.append("START")
                if not (btn1 & 0x10): buttons.append("UP")
                if not (btn1 & 0x20): buttons.append("RIGHT")
                if not (btn1 & 0x40): buttons.append("DOWN")
                if not (btn1 & 0x80): buttons.append("LEFT")
                
                if not (btn2 & 0x10): buttons.append("TRIANGLE")
                if not (btn2 & 0x20): buttons.append("CIRCLE")
                if not (btn2 & 0x40): buttons.append("CROSS")
                if not (btn2 & 0x80): buttons.append("SQUARE")
                
                if buttons:
                    print(f"   Кнопки: {', '.join(buttons)}")
                else:
                    print("   Кнопки: не нажаты")
                
                # Стики (байты 3-6)
                if len(responses) >= 7:
                    lx = responses[3]
                    ly = responses[4]
                    rx = responses[5]
                    ry = responses[6]
                    print(f"   Левый стик: X={lx:3d}, Y={ly:3d}")
                    print(f"   Правый стик: X={rx:3d}, Y={ry:3d}")
            
            time.sleep(0.05)  # 20 раз в секунду
            
    except KeyboardInterrupt:
        print("\n   Тест завершен")

def main():
    """Главная функция"""
    print("Простейший тест PS2 геймпада для Raspberry Pi")
    
    try:
        # Настройка
        setup()
        
        # Тест контроллера
        if test_controller():
            # Тест кнопок
            read_buttons()
        else:
            print("\n✗ Контроллер не найден или не отвечает")
            print("\nПРОВЕРЬТЕ:")
            print("1. Подключение проводов:")
            print("   Оранжевый -> Pin 18")
            print("   Синий     -> Pin 15")
            print("   Зеленый   -> Pin 16")
            print("   Фиолетовый-> Pin 13")
            print("   Красный   -> 3.3V (Pin 1)")
            print("   Черный    -> GND (Pin 6)")
            print("\n2. На контроллере:")
            print("   - Должен гореть красный светодиод")
            print("   - Нажмите кнопку Analog/Mode")
            print("   - Попробуйте другой контроллер")
            
    except KeyboardInterrupt:
        print("\n\nТест отменен")
    except Exception as e:
        print(f"\nОшибка: {e}")
    finally:
        GPIO.cleanup()
        print("\nГотово!")

if __name__ == "__main__":
    # Проверка запуска от root
    import os
    if os.geteuid() != 0:
        print("Запустите с sudo:")
        print("  sudo python3 simple_test.py")
    else:
        main()