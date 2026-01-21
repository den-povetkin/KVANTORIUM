#!/usr/bin/env python3
"""
Тестирование PS2 контроллера с библиотекой gpiozero
Запуск: sudo python3 test_ps2_gpiozero.py
"""

import sys
import time
import signal
from ps2_controller_gpiozero import PS2ControllerGPIOZero

def signal_handler(sig, frame):
    """Обработчик Ctrl+C"""
    print("\n\n[INFO] Завершение программы...")
    sys.exit(0)

def test_basic_functionality():
    """Тест базовой функциональности"""
    print("\n" + "="*60)
    print("ТЕСТ БАЗОВОЙ ФУНКЦИОНАЛЬНОСТИ")
    print("="*60)
    
    # Создаем контроллер с кастомными пинами
    controller = PS2ControllerGPIOZero(
        data_pin=17,  # GPIO17, Pin 11
        cmd_pin=18,   # GPIO18, Pin 12
        att_pin=27,   # GPIO27, Pin 13
        clk_pin=22,   # GPIO22, Pin 15
        polling_rate=50
    )
    
    if not controller.connected:
        print("[ERROR] Контроллер не подключен!")
        return False
    
    print("[INFO] Тестирование кнопок. Нажмите несколько кнопок...")
    print("[INFO] Нажмите START для завершения теста")
    
    test_duration = 30  # секунд
    start_time = time.time()
    last_print = 0
    
    try:
        while time.time() - start_time < test_duration:
            current_time = time.time()
            
            # Выводим состояние каждые 0.1 секунды
            if current_time - last_print >= 0.1:
                # Проверяем кнопку START для досрочного завершения
                if controller.is_pressed(controller.BUTTON_START):
                    print("\n[INFO] Нажата кнопка START, завершение теста")
                    break
                
                # Проверяем другие кнопки
                pressed_buttons = []
                for i in range(16):
                    if controller.was_pressed(i):
                        pressed_buttons.append(controller.BUTTON_NAMES[i])
                
                if pressed_buttons:
                    print(f"[TEST] Нажаты кнопки: {', '.join(pressed_buttons)}")
                
                last_print = current_time
            
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n[INFO] Тест прерван пользователем")
    
    finally:
        controller.cleanup()
    
    return True

def test_analog_precision():
    """Тест точности аналоговых стиков"""
    print("\n" + "="*60)
    print("ТЕСТ АНАЛОГОВЫХ СТИКОВ")
    print("="*60)
    
    controller = PS2ControllerGPIOZero(polling_rate=100)
    
    if not controller.connected:
        print("[ERROR] Контроллер не подключен!")
        return False
    
    print("[INFO] Двигайте аналоговые стики в разные положения")
    print("[INFO] Нажмите SELECT для калибровки центра")
    print("[INFO] Нажмите START для завершения")
    
    # Калибровочные значения
    calibration = {
        'lx': [], 'ly': [],
        'rx': [], 'ry': []
    }
    
    try:
        while True:
            # Проверяем кнопки управления
            if controller.was_pressed(controller.BUTTON_START):
                print("\n[INFO] Завершение теста")
                break
            
            if controller.was_pressed(controller.BUTTON_SELECT):
                # Собираем калибровочные данные
                print("\n[INFO] Калибровка... отпустите стики")
                time.sleep(1)
                
                samples = []
                for _ in range(50):
                    samples.append({
                        'lx': controller.get_analog('lx'),
                        'ly': controller.get_analog('ly'),
                        'rx': controller.get_analog('rx'),
                        'ry': controller.get_analog('ry')
                    })
                    time.sleep(0.01)
                
                # Вычисляем средние значения
                avg = {k: sum(s[k] for s in samples) / len(samples) 
                      for k in samples[0].keys()}
                
                print(f"[CALIBRATION] Центральные значения:")
                print(f"  Left Stick:  X={avg['lx']:.1f}, Y={avg['ly']:.1f}")
                print(f"  Right Stick: X={avg['rx']:.1f}, Y={avg['ry']:.1f}")
            
            # Выводим текущие значения
            output = controller.get_formatted_output()
            print("\033[H\033[J")  # Очистка экрана
            print(output)
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n[INFO] Тест прерван")
    
    finally:
        controller.cleanup()
    
    return True

def test_performance():
    """Тест производительности"""
    print("\n" + "="*60)
    print("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("="*60)
    
    test_durations = [30, 60]  # секунд
    polling_rates = [30, 50, 100]  # Гц
    
    results = {}
    
    for rate in polling_rates:
        print(f"\n[TEST] Тестирование с частотой опроса {rate} Гц")
        
        controller = PS2ControllerGPIOZero(polling_rate=rate)
        
        if not controller.connected:
            print(f"[ERROR] Контроллер не подключен для частоты {rate} Гц")
            continue
        
        # Ждем стабилизации
        time.sleep(1)
        
        # Сбрасываем счетчики
        controller.read_count = 0
        controller.error_count = 0
        
        # Тестируем
        test_start = time.time()
        
        try:
            while time.time() - test_start < test_durations[0]:
                # Просто читаем данные
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("[INFO] Тест прерван")
        
        finally:
            # Собираем статистику
            stats = controller.get_stats()
            results[rate] = stats
            
            print(f"[RESULTS] Частота: {rate} Гц")
            print(f"          Успешных чтений: {stats['read_count']}")
            print(f"          Ошибок: {stats['error_count']}")
            print(f"          Успешность: {stats['success_rate']:.1f}%")
            
            controller.cleanup()
    
    # Сводка результатов
    print("\n" + "="*60)
    print("СВОДКА РЕЗУЛЬТАТОВ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("="*60)
    
    for rate, stats in results.items():
        print(f"{rate:3d} Гц: {stats['success_rate']:6.1f}% успеха, "
              f"{stats['read_count']:5d} чтений, {stats['error_count']:3d} ошибок")
    
    return True

def interactive_test():
    """Интерактивный тест с меню"""
    print("\n" + "="*60)
    print("ИНТЕРАКТИВНЫЙ ТЕСТ PS2 КОНТРОЛЛЕРА")
    print("="*60)
    
    # Инициализируем контроллер
    controller = PS2ControllerGPIOZero(polling_rate=50)
    
    if not controller.connected:
        print("[ERROR] Контроллер не подключен!")
        return False
    
    print("\n[INFO] Контроллер инициализирован")
    print("[INFO] Используйте следующие кнопки для управления:")
    print("       TRIANGLE - Показать/скрыть подробный вывод")
    print("       CIRCLE   - Тест вибрации (если поддерживается)")
    print("       CROSS    - Сброс статистики")
    print("       SQUARE   - Переключение режима вывода")
    print("       START    - Выход")
    
    detailed_view = True
    show_stats = True
    
    try:
        while True:
            # Проверяем кнопки управления
            if controller.was_pressed(controller.BUTTON_START):
                print("\n[INFO] Выход из интерактивного теста")
                break
            
            if controller.was_pressed(controller.BUTTON_TRIANGLE):
                detailed_view = not detailed_view
                print(f"\n[INFO] Подробный вывод: {'ВКЛ' if detailed_view else 'ВЫКЛ'}")
            
            if controller.was_pressed(controller.BUTTON_CROSS):
                controller.read_count = 0
                controller.error_count = 0
                print("\n[INFO] Статистика сброшена")
            
            if controller.was_pressed(controller.BUTTON_SQUARE):
                show_stats = not show_stats
                print(f"\n[INFO] Показать статистику: {'ВКЛ' if show_stats else 'ВЫКЛ'}")
            
            # Выводим состояние
            if detailed_view:
                output = controller.get_formatted_output()
                print("\033[H\033[J")  # Очистка экрана
                print(output)
            else:
                # Компактный вывод
                pressed = [controller.BUTTON_NAMES[i] 
                          for i in range(16) 
                          if controller.is_pressed(i)]
                
                analog = controller.get_all_analog()
                
                print("\033[H\033[J")  # Очистка экрана
                print("PS2 Controller - Compact View")
                print("-" * 40)
                
                if pressed:
                    print(f"Pressed: {', '.join(pressed)}")
                else:
                    print("No buttons pressed")
                
                print(f"Left: ({analog['lx']:3d},{analog['ly']:3d}) "
                      f"Right: ({analog['rx']:3d},{analog['ry']:3d})")
                
                if show_stats:
                    stats = controller.get_stats()
                    print(f"Rate: {stats['success_rate']:.1f}%")
            
            # Небольшая задержка для плавности
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n[INFO] Тест прерван")
    
    finally:
        # Финальная статистика
        stats = controller.get_stats()
        print("\n" + "="*60)
        print("ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"Всего чтений: {stats['read_count']}")
        print(f"Ошибок: {stats['error_count']}")
        print(f"Успешность: {stats['success_rate']:.1f}%")
        print("="*60)
        
        controller.cleanup()
    
    return True

def main():
    """Главная функция"""
    # Настраиваем обработчик Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print("ТЕСТИРОВАНИЕ PS2 КОНТРОЛЛЕРА С GPIOZERO")
    print("Версия: 1.0")
    print("Подключение:")
    print("  DATA  -> GPIO17 (Pin 11)")
    print("  CMD   -> GPIO18 (Pin 12)")
    print("  ATT   -> GPIO27 (Pin 13)")
    print("  CLK   -> GPIO22 (Pin 15)")
    print("  VCC   -> 3.3V   (Pin 1)")
    print("  GND   -> GND    (Pin 6)")
    print("-" * 60)
    
    # Меню выбора теста
    while True:
        print("\nВыберите тест:")
        print("1. Базовая функциональность")
        print("2. Аналоговые стики")
        print("3. Производительность")
        print("4. Интерактивный тест")
        print("5. Все тесты")
        print("0. Выход")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "0":
            print("Выход...")
            break
        
        elif choice == "1":
            test_basic_functionality()
        
        elif choice == "2":
            test_analog_precision()
        
        elif choice == "3":
            test_performance()
        
        elif choice == "4":
            interactive_test()
        
        elif choice == "5":
            print("\nЗапуск всех тестов...")
            test_basic_functionality()
            time.sleep(2)
            test_analog_precision()
            time.sleep(2)
            test_performance()
            time.sleep(2)
            interactive_test()
        
        else:
            print("Неверный выбор. Попробуйте снова.")
    
    print("\n[INFO] Тестирование завершено!")

if __name__ == "__main__":
    # Проверка прав
    import os
    if os.geteuid() != 0:
        print("[WARNING] Рекомендуется запускать с sudo для доступа к GPIO")
        print("          Запустите: sudo python3 test_ps2_gpiozero.py")
        response = input("Продолжить без sudo? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    
    main()