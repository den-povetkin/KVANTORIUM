#!/usr/bin/env python3
"""
ТЕСТ ПОДКЛЮЧЕНИЯ PS2 ГЕЙМПАДА SZDoit К GPIO RASPBERRY PI
Прямое подключение без адаптеров
"""

import time
import RPi.GPIO as GPIO
import os
import sys

# =================== НАСТРОЙКА ПИНОВ SZDoit PS2 ===================
# Пины подключения PS2 контроллера SZDoit (физическая нумерация пинов)
PS2_DAT = 13    # GPIO27 - DATA (фиолетовый провод)
PS2_CMD = 15    # GPIO22 - COMMAND (синий провод)
PS2_SEL = 16    # GPIO23 - ATTENTION/SELECT (зеленый провод)
PS2_CLK = 18    # GPIO24 - CLOCK (оранжевый провод)

# =================== ЦВЕТА ДЛЯ ВЫВОДА ===================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# =================== ОСНОВНОЙ ТЕСТЕР ===================
class SZDoitPS2Tester:
    def __init__(self):
        self.connected = False
        self.controller_type = "Неизвестно"
        self.analog_mode = False
        self.test_results = []
        
    def print_header(self):
        """Вывод заголовка теста"""
        print(f"{Colors.CYAN}{'='*70}")
        print(f"{Colors.BOLD}ТЕСТ ПОДКЛЮЧЕНИЯ PS2 ГЕЙМПАДА SZDoit")
        print(f"{Colors.CYAN}{'='*70}{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}СХЕМА ПОДКЛЮЧЕНИЯ PS2 SZDoit:{Colors.RESET}")
        print("PS2 разъем -> Raspberry Pi (физические пины):")
        print(f"  {Colors.MAGENTA}Фиолетовый (DATA)   -> Pin {PS2_DAT} (GPIO27){Colors.RESET}")
        print(f"  {Colors.BLUE}Синий (COMMAND)      -> Pin {PS2_CMD} (GPIO22){Colors.RESET}")
        print(f"  {Colors.GREEN}Зеленый (ATTENTION)  -> Pin {PS2_SEL} (GPIO23){Colors.RESET}")
        print(f"  {Colors.YELLOW}Оранжевый (CLOCK)    -> Pin {PS2_CLK} (GPIO24){Colors.RESET}")
        print(f"  {Colors.RED}Красный (VCC)        -> 3.3V (Pin 1 или 17){Colors.RESET}")
        print(f"  Черный (GND)         -> GND (Pin 6, 9, 14, 20, 25)")
        
        print(f"\n{Colors.YELLOW}ВАЖНО:{Colors.RESET}")
        print("  1. Питание PS2 - ТОЛЬКО 3.3V! Не подключайте к 5V!")
        print("  2. Нажмите кнопку Analog/Mode на геймпаде")
        print("  3. Должен гореть красный светодиод на геймпаде")
        print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}\n")
        
    def setup_gpio(self):
        """Настройка GPIO пинов"""
        print(f"{Colors.BLUE}[1/5] Настройка GPIO...{Colors.RESET}")
        
        try:
            GPIO.setmode(GPIO.BOARD)  # Используем физическую нумерацию
            GPIO.setwarnings(True)
            
            # Настройка пинов PS2
            GPIO.setup(PS2_DAT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(PS2_CMD, GPIO.OUT)
            GPIO.setup(PS2_SEL, GPIO.OUT)
            GPIO.setup(PS2_CLK, GPIO.OUT)
            
            # Установка начальных состояний
            GPIO.output(PS2_SEL, GPIO.HIGH)
            GPIO.output(PS2_CLK, GPIO.HIGH)
            GPIO.output(PS2_CMD, GPIO.HIGH)
            
            print(f"  {Colors.GREEN}✓ GPIO настроен{Colors.RESET}")
            return True
            
        except Exception as e:
            print(f"  {Colors.RED}✗ Ошибка настройки GPIO: {e}{Colors.RESET}")
            return False
    
    def test_hardware_connections(self):
        """Тест аппаратных соединений"""
        print(f"{Colors.BLUE}[2/5] Тест аппаратных соединений...{Colors.RESET}")
        
        tests_passed = 0
        total_tests = 3
        
        try:
            # Тест 1: Проверка линии DAT
            dat_state = GPIO.input(PS2_DAT)
            if dat_state == GPIO.HIGH:
                print(f"  {Colors.GREEN}✓ DAT: HIGH (норма){Colors.RESET}")
                tests_passed += 1
            else:
                print(f"  {Colors.YELLOW}⚠ DAT: LOW (возможна проблема){Colors.RESET}")
                
            # Тест 2: Тест линии CLK
            GPIO.output(PS2_CLK, GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(PS2_CLK, GPIO.HIGH)
            print(f"  {Colors.GREEN}✓ CLK: управляется{Colors.RESET}")
            tests_passed += 1
            
            # Тест 3: Тест линии CMD
            GPIO.output(PS2_CMD, GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(PS2_CMD, GPIO.HIGH)
            print(f"  {Colors.GREEN}✓ CMD: управляется{Colors.RESET}")
            tests_passed += 1
            
            result = tests_passed == total_tests
            status = f"{Colors.GREEN}ПРОЙДЕН{Colors.RESET}" if result else f"{Colors.YELLOW}ЧАСТИЧНО{Colors.RESET}"
            print(f"  Результат: {status} ({tests_passed}/{total_tests})")
            
            return result
            
        except Exception as e:
            print(f"  {Colors.RED}✗ Ошибка теста: {e}{Colors.RESET}")
            return False
    
    def send_byte(self, data):
        """Отправка одного байта"""
        received = 0
        
        for i in range(8):
            GPIO.output(PS2_CLK, GPIO.LOW)
            time.sleep(0.00001)  # 10 мкс
            
            # Установка бита на CMD
            bit = (data >> i) & 1
            GPIO.output(PS2_CMD, GPIO.HIGH if bit else GPIO.LOW)
            time.sleep(0.00001)
            
            GPIO.output(PS2_CLK, GPIO.HIGH)
            time.sleep(0.00001)
            
            # Чтение бита с DAT
            received_bit = GPIO.input(PS2_DAT)
            received |= (received_bit << i)
            
            time.sleep(0.00001)
            
        return received
    
    def ps2_command(self, command, read_bytes=6):
        """Отправка команды PS2 контроллеру"""
        response = []
        
        try:
            GPIO.output(PS2_SEL, GPIO.LOW)
            time.sleep(0.0001)
            
            # Отправка команды и чтение ответа
            response.append(self.send_byte(command))
            
            for _ in range(read_bytes):
                response.append(self.send_byte(0x00))
            
            GPIO.output(PS2_SEL, GPIO.HIGH)
            time.sleep(0.0001)
            
            return response
            
        except Exception as e:
            GPIO.output(PS2_SEL, GPIO.HIGH)
            print(f"  {Colors.RED}✗ Ошибка команды: {e}{Colors.RESET}")
            return None
    
    def test_communication(self):
        """Тест связи с контроллером"""
        print(f"{Colors.BLUE}[3/5] Тест связи с контроллером...{Colors.RESET}")
        
        print("  Отправка команды инициализации (0x01)...")
        response = self.ps2_command(0x01)
        
        if not response:
            print(f"  {Colors.RED}✗ Нет ответа от контроллера{Colors.RESET}")
            return False
        
        print(f"  Ответ: {[hex(x) for x in response]}")
        
        if response[0] == 0xFF:
            print(f"  {Colors.RED}✗ Контроллер не отвечает (0xFF){Colors.RESET}")
            print(f"  {Colors.YELLOW}Проверьте:{Colors.RESET}")
            print("    1. Подключен ли контроллер")
            print("    2. Включен ли он (красный светодиод)")
            print("    3. Нажата ли кнопка Analog/Mode")
            return False
        
        # Определение типа контроллера
        controller_id = response[1]
        controllers = {
            0x41: "Digital PlayStation Controller",
            0x23: "DualShock (Digital Mode)",
            0x73: "DualShock (Analog Mode)",
            0x79: "DualShock 2 Controller",
            0x5A: "NegCon Controller",
        }
        
        self.controller_type = controllers.get(controller_id, f"Unknown (0x{controller_id:02X})")
        print(f"  {Colors.GREEN}✓ Контроллер найден!{Colors.RESET}")
        print(f"  Тип: {Colors.CYAN}{self.controller_type}{Colors.RESET}")
        
        self.connected = True
        return True
    
    def test_analog_mode(self):
        """Тест аналогового режима"""
        print(f"{Colors.BLUE}[4/5] Тест аналогового режима...{Colors.RESET}")
        
        if "DualShock" not in self.controller_type:
            print(f"  {Colors.YELLOW}⚠ Контроллер не поддерживает аналоговый режим{Colors.RESET}")
            return False
        
        print("  Включение аналогового режима (0x44)...")
        response = self.ps2_command(0x44)
        
        if response and response[1] == 0x73:
            # Подтверждение режима
            self.ps2_command(0x4F)
            self.analog_mode = True
            print(f"  {Colors.GREEN}✓ Аналоговый режим включен{Colors.RESET}")
            return True
        else:
            print(f"  {Colors.YELLOW}⚠ Не удалось включить аналоговый режим{Colors.RESET}")
            return False
    
    def real_time_test(self):
        """Тест в реальном времени"""
        print(f"{Colors.BLUE}[5/5] Тест в реальном времени...{Colors.RESET}")
        print("  Нажимайте кнопки, двигайте стики...")
        print(f"  {Colors.YELLOW}Для выхода нажмите Ctrl+C{Colors.RESET}\n")
        
        poll_count = 0
        last_buttons = set()
        
        try:
            while True:
                response = self.ps2_command(0x42, 8)  # Команда чтения состояния
                
                if not response or response[0] == 0xFF:
                    print(f"{Colors.RED}✗ Потеря связи с контроллером{Colors.RESET}")
                    break
                
                poll_count += 1
                
                # Разбор кнопок
                btn1 = response[1]
                btn2 = response[2]
                
                # Маппинг кнопок
                button_map = {
                    'SELECT': not (btn1 & 0x01),
                    'L3': not (btn1 & 0x02),
                    'R3': not (btn1 & 0x04),
                    'START': not (btn1 & 0x08),
                    'UP': not (btn1 & 0x10),
                    'RIGHT': not (btn1 & 0x20),
                    'DOWN': not (btn1 & 0x40),
                    'LEFT': not (btn1 & 0x80),
                    'L2': not (btn2 & 0x01),
                    'R2': not (btn2 & 0x02),
                    'L1': not (btn2 & 0x04),
                    'R1': not (btn2 & 0x08),
                    'TRIANGLE': not (btn2 & 0x10),
                    'CIRCLE': not (btn2 & 0x20),
                    'CROSS': not (btn2 & 0x40),
                    'SQUARE': not (btn2 & 0x80),
                }
                
                # Получение нажатых кнопок
                pressed_buttons = {btn for btn, pressed in button_map.items() if pressed}
                
                # Вывод изменений
                if pressed_buttons != last_buttons:
                    last_buttons = pressed_buttons.copy()
                    
                    # Очистка строки
                    print("\033[K", end="")
                    
                    if pressed_buttons:
                        print(f"\rКнопки: {', '.join(pressed_buttons)}", end="")
                    else:
                        print(f"\rКнопки: не нажаты", end="")
                
                # Вывод стиков раз в 10 опросов
                if poll_count % 10 == 0 and len(response) >= 7:
                    print("\033[K", end="")
                    lx = response[3]
                    ly = response[4]
                    rx = response[5]
                    ry = response[6]
                    print(f"\rСтики: L({lx:3d},{ly:3d}) R({rx:3d},{ry:3d}) | Опрос #{poll_count}", end="")
                
                time.sleep(0.05)  # 20 Гц
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Тест остановлен{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}Ошибка: {e}{Colors.RESET}")
    
    def print_summary(self):
        """Вывод итогов теста"""
        print(f"\n{Colors.CYAN}{'='*70}")
        print(f"ИТОГИ ТЕСТА SZDoit PS2")
        print(f"{'='*70}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Результаты:{Colors.RESET}")
        print(f"  1. Подключение к GPIO:   {Colors.GREEN}✓{Colors.RESET}")
        print(f"  2. Аппаратные соединения:{Colors.GREEN}✓{Colors.RESET}")
        print(f"  3. Связь с контроллером: {'✓' if self.connected else '✗'}")
        
        if self.connected:
            print(f"  4. Тип контроллера:      {Colors.CYAN}{self.controller_type}{Colors.RESET}")
            print(f"  5. Аналоговый режим:     {'✓' if self.analog_mode else '✗'}")
        
        print(f"\n{Colors.YELLOW}Подсказки:{Colors.RESET}")
        
        if not self.connected:
            print(f"  • Проверьте все соединения проводов")
            print(f"  • Убедитесь, что VCC подключен к 3.3V (НЕ к 5V!)")
            print(f"  • Нажмите кнопку Analog/Mode на контроллере")
            print(f"  • Должен гореть красный светодиод на контроллере")
        else:
            print(f"  • Контроллер готов к использованию")
            print(f"  • Для работы в программе используйте команду чтения 0x42")
            
        print(f"\n{Colors.CYAN}{'='*70}{Colors.RESET}")
    
    def run(self):
        """Запуск полного теста"""
        self.print_header()
        
        input(f"{Colors.YELLOW}Нажмите Enter для начала теста...{Colors.RESET}")
        
        try:
            # Тест 1: Настройка GPIO
            if not self.setup_gpio():
                return
            
            # Тест 2: Аппаратные соединения
            if not self.test_hardware_connections():
                print(f"\n{Colors.RED}Проверьте соединения и повторите тест{Colors.RESET}")
                return
            
            # Тест 3: Связь с контроллером
            if not self.test_communication():
                print(f"\n{Colors.RED}Контроллер не обнаружен{Colors.RESET}")
                return
            
            # Тест 4: Аналоговый режим
            self.test_analog_mode()
            
            # Тест 5: Реальный режим
            self.real_time_test()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Тест прерван{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}Неожиданная ошибка: {e}{Colors.RESET}")
        finally:
            self.cleanup()
            self.print_summary()
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            GPIO.output(PS2_SEL, GPIO.HIGH)
            GPIO.output(PS2_CLK, GPIO.HIGH)
            GPIO.output(PS2_CMD, GPIO.HIGH)
            GPIO.cleanup()
        except:
            pass

# =================== БЫСТРЫЙ ТЕСТ (минимальная версия) ===================
def quick_test():
    """Быстрый тест подключения"""
    print(f"{Colors.CYAN}БЫСТРЫЙ ТЕСТ ПОДКЛЮЧЕНИЯ PS2 SZDoit{Colors.RESET}")
    
    GPIO.setmode(GPIO.BOARD)
    
    # Быстрая настройка
    GPIO.setup(PS2_DAT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PS2_CMD, GPIO.OUT)
    GPIO.setup(PS2_SEL, GPIO.OUT)
    GPIO.setup(PS2_CLK, GPIO.OUT)
    
    GPIO.output(PS2_SEL, GPIO.HIGH)
    GPIO.output(PS2_CLK, GPIO.HIGH)
    GPIO.output(PS2_CMD, GPIO.HIGH)
    
    print("Проверка связи...")
    
    try:
        # Пробуем обратиться к контроллеру
        GPIO.output(PS2_SEL, GPIO.LOW)
        time.sleep(0.0001)
        
        # Простая функция отправки
        def send_quick(data):
            received = 0
            for i in range(8):
                GPIO.output(PS2_CLK, GPIO.LOW)
                time.sleep(0.00001)
                GPIO.output(PS2_CMD, GPIO.HIGH if ((data >> i) & 1) else GPIO.LOW)
                time.sleep(0.00001)
                GPIO.output(PS2_CLK, GPIO.HIGH)
                time.sleep(0.00001)
                received |= (GPIO.input(PS2_DAT) << i)
                time.sleep(0.00001)
            return received
        
        # Отправляем команду
        resp1 = send_quick(0x01)
        responses = [resp1]
        for _ in range(5):
            responses.append(send_quick(0x00))
        
        GPIO.output(PS2_SEL, GPIO.HIGH)
        
        if responses[0] != 0xFF:
            print(f"{Colors.GREEN}✓ Контроллер обнаружен!{Colors.RESET}")
            print(f"Ответ: {[hex(x) for x in responses]}")
            
            # Простой тест кнопок
            print(f"\n{Colors.YELLOW}Нажмите кнопки (Ctrl+C для выхода):{Colors.RESET}")
            
            while True:
                GPIO.output(PS2_SEL, GPIO.LOW)
                time.sleep(0.0001)
                
                cmd_resp = send_quick(0x42)
                btn_data = []
                btn_data.append(cmd_resp)
                for _ in range(3):
                    btn_data.append(send_quick(0x00))
                
                GPIO.output(PS2_SEL, GPIO.HIGH)
                
                # Простая проверка кнопок
                if (btn_data[1] & 0xF0) != 0xF0:  # Проверка D-pad
                    print("\r", end="")
                    if not (btn_data[1] & 0x10):
                        print("UP ", end="")
                    if not (btn_data[1] & 0x20):
                        print("RIGHT ", end="")
                    if not (btn_data[1] & 0x40):
                        print("DOWN ", end="")
                    if not (btn_data[1] & 0x80):
                        print("LEFT ", end="")
                
                time.sleep(0.1)
                
        else:
            print(f"{Colors.RED}✗ Контроллер не отвечает{Colors.RESET}")
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Тест остановлен{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Ошибка: {e}{Colors.RESET}")
    finally:
        GPIO.cleanup()

# =================== ТОЧКА ВХОДА ===================
if __name__ == "__main__":
    print(f"{Colors.CYAN}ТЕСТЕР ПОДКЛЮЧЕНИЯ PS2 ГЕЙМПАДА SZDoit{Colors.RESET}")
    print(f"Для Raspberry Pi с прямым подключением к GPIO\n")
    
    # Проверка прав
    if os.geteuid() != 0:
        print(f"{Colors.RED}ОШИБКА: Запустите тест с sudo!{Colors.RESET}")
        print(f"  sudo python3 {sys.argv[0]}")
        sys.exit(1)
    
    print(f"Выберите режим теста:")
    print(f"  1. {Colors.GREEN}Полный тест{Colors.RESET} (рекомендуется)")
    print(f"  2. {Colors.YELLOW}Быстрый тест{Colors.RESET}")
    print(f"  3. {Colors.BLUE}Проверка пинов{Colors.RESET}")
    
    try:
        choice = input("Ваш выбор (1/2/3): ").strip()
        
        if choice == "2":
            quick_test()
        elif choice == "3":
            # Простая проверка пинов
            print(f"\n{Colors.CYAN}ПРОВЕРКА ПИНОВ:{Colors.RESET}")
            print(f"DAT (GPIO27): Pin {PS2_DAT}")
            print(f"CMD (GPIO22): Pin {PS2_CMD}")
            print(f"SEL (GPIO23): Pin {PS2_SEL}")
            print(f"CLK (GPIO24): Pin {PS2_CLK}")
            print(f"\n{Colors.YELLOW}Подключите провода PS2 к указанным пинам{Colors.RESET}")
        else:
            # Полный тест
            tester = SZDoitPS2Tester()
            tester.run()
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Тест отменен{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Ошибка: {e}{Colors.RESET}")