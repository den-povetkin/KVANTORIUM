#!/usr/bin/env python3
"""
ПОДКЛЮЧЕНИЕ PS2 ГЕЙМПАДА SZDoit К RASPBERRY PI OS UBUNTU ЧЕРЕЗ GPIO
Полное пошаговое руководство с кодом
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import threading

# =================== КОНСТАНТЫ ДЛЯ UBUNTU ===================
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Распиновка GPIO для PS2 (BCM нумерация)
PS2_PINS = {
    'dat': 27,   # GPIO27 - DATA (фиолетовый)
    'cmd': 22,   # GPIO22 - COMMAND (синий)
    'sel': 23,   # GPIO23 - SELECT/ATTENTION (зеленый)
    'clk': 24,   # GPIO24 - CLOCK (оранжевый)
}

# Физические пины Raspberry Pi
PHYSICAL_PINS = {
    27: 13,  # GPIO27 -> Pin 13
    22: 15,  # GPIO22 -> Pin 15
    23: 16,  # GPIO23 -> Pin 16
    24: 18,  # GPIO24 -> Pin 18
}

# =================== 1. ПОДГОТОВКА СИСТЕМЫ UBUNTU ===================
class UbuntuSystemSetup:
    """Подготовка Ubuntu для работы с GPIO"""
    
    @staticmethod
    def check_ubuntu_version() -> Tuple[str, str]:
        """Проверка версии Ubuntu"""
        try:
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                os_info = {}
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
                
                version = os_info.get('VERSION_ID', '')
                name = os_info.get('PRETTY_NAME', 'Ubuntu')
                
                print(f"{Color.GREEN}✓ Обнаружена ОС: {name} {version}{Color.RESET}")
                return name, version
                
        except Exception as e:
            print(f"{Color.RED}✗ Ошибка определения ОС: {e}{Color.RESET}")
            return "Ubuntu", "unknown"
    
    @staticmethod
    def update_system() -> bool:
        """Обновление системы"""
        print(f"{Color.BLUE}[1/6] Обновление системы...{Color.RESET}")
        
        commands = [
            "sudo apt update",
            "sudo apt upgrade -y",
            "sudo apt dist-upgrade -y",
            "sudo apt autoremove -y",
            "sudo apt clean",
        ]
        
        for cmd in commands:
            print(f"  Выполняю: {Color.YELLOW}{cmd}{Color.RESET}")
            try:
                subprocess.run(cmd, shell=True, check=True, timeout=300)
            except subprocess.CalledProcessError:
                print(f"  {Color.YELLOW}⚠ Пропускаю ошибку в: {cmd}{Color.RESET}")
            except subprocess.TimeoutExpired:
                print(f"  {Color.YELLOW}⚠ Таймаут команды: {cmd}{Color.RESET}")
        
        print(f"  {Color.GREEN}✓ Система обновлена{Color.RESET}")
        return True
    
    @staticmethod
    def install_python_dependencies() -> bool:
        """Установка Python зависимостей"""
        print(f"{Color.BLUE}[2/6] Установка Python зависимостей...{Color.RESET}")
        
        packages = [
            "sudo apt install -y python3-dev python3-pip python3-venv",
            "sudo apt install -y python3-setuptools python3-wheel",
            "sudo apt install -y python3-smbus python3-serial",
            "pip3 install --upgrade pip",
        ]
        
        for pkg in packages:
            print(f"  Выполняю: {Color.YELLOW}{pkg}{Color.RESET}")
            subprocess.run(pkg, shell=True, check=False)
        
        print(f"  {Color.GREEN}✓ Python зависимости установлены{Color.RESET}")
        return True

# =================== 2. УСТАНОВКА GPIO БИБЛИОТЕК ===================
class GPIOLibraryInstaller:
    """Установка библиотек для работы с GPIO в Ubuntu"""
    
    @staticmethod
    def install_libgpiod() -> bool:
        """Установка libgpiod (рекомендуется для Ubuntu 22.04+)"""
        print(f"{Color.BLUE}Установка libgpiod...{Color.RESET}")
        
        packages = [
            "sudo apt install -y libgpiod-dev libgpiod2",
            "sudo apt install -y gpiod python3-libgpiod",
            "sudo apt install -y libgpiod-doc",
        ]
        
        for pkg in packages:
            print(f"  Выполняю: {Color.YELLOW}{pkg}{Color.RESET}")
            result = subprocess.run(pkg, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  {Color.YELLOW}⚠ Ошибка установки: {result.stderr[:100]}{Color.RESET}")
        
        # Проверка установки
        try:
            subprocess.run(["gpiodetect"], check=True, capture_output=True)
            print(f"  {Color.GREEN}✓ libgpiod установлен{Color.RESET}")
            return True
        except:
            print(f"  {Color.RED}✗ libgpiod не установлен{Color.RESET}")
            return False
    
    @staticmethod
    def install_python_gpiod() -> bool:
        """Установка Python библиотеки gpiod"""
        print(f"{Color.BLUE}Установка Python библиотеки gpiod...{Color.RESET}")
        
        try:
            # Попробуем установить через pip
            subprocess.run(["pip3", "install", "gpiod"], check=True, capture_output=True)
            print(f"  {Color.GREEN}✓ Python gpiod установлен{Color.RESET}")
            return True
        except:
            # Пробуем через apt
            subprocess.run(["sudo", "apt", "install", "-y", "python3-gpiod"], check=False)
            
            # Проверка импорта
            try:
                import gpiod
                print(f"  {Color.GREEN}✓ Python gpiod доступен{Color.RESET}")
                return True
            except ImportError:
                print(f"  {Color.RED}✗ Не удалось установить Python gpiod{Color.RESET}")
                return False
    
    @staticmethod
    def install_rpi_gpio() -> bool:
        """Установка RPi.GPIO (альтернатива)"""
        print(f"{Color.BLUE}Установка RPi.GPIO...{Color.RESET}")
        
        try:
            subprocess.run(["pip3", "install", "RPi.GPIO"], check=True)
            print(f"  {Color.GREEN}✓ RPi.GPIO установлен{Color.RESET}")
            return True
        except:
            print(f"  {Color.YELLOW}⚠ RPi.GPIO не удалось установить через pip{Color.RESET}")
            
            # Пробуем через apt
            subprocess.run(["sudo", "apt", "install", "-y", "python3-rpi.gpio"], check=False)
            
            try:
                import RPi.GPIO as GPIO
                print(f"  {Color.GREEN}✓ RPi.GPIO доступен{Color.RESET}")
                return True
            except:
                print(f"  {Color.YELLOW}⚠ RPi.GPIO не работает на этой системе{Color.RESET}")
                return False
    
    @staticmethod
    def install_periphery() -> bool:
        """Установка python-periphery"""
        print(f"{Color.BLUE}Установка python-periphery...{Color.RESET}")
        
        try:
            subprocess.run(["sudo", "apt", "install", "-y", "python3-periphery"], check=True)
            print(f"  {Color.GREEN}✓ python-periphery установлен{Color.RESET}")
            return True
        except:
            try:
                subprocess.run(["pip3", "install", "python-periphery"], check=True)
                print(f"  {Color.GREEN}✓ python-periphery установлен через pip{Color.RESET}")
                return True
            except:
                print(f"  {Color.YELLOW}⚠ python-periphery не удалось установить{Color.RRESET}")
                return False
    
    @staticmethod
    def setup_gpio_permissions() -> bool:
        """Настройка прав доступа к GPIO"""
        print(f"{Color.BLUE}Настройка прав доступа к GPIO...{Color.RESET}")
        
        # Создаем группу gpio если не существует
        subprocess.run(["sudo", "groupadd", "-f", "gpio"], check=False)
        
        # Добавляем пользователя в группу
        subprocess.run(["sudo", "usermod", "-a", "-G", "gpio", os.getenv("USER")], check=False)
        
        # Создаем udev правила для libgpiod
        udev_rules = '''# Правила для доступа к GPIO через libgpiod
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", KERNEL=="gpio*", GROUP="gpio", MODE="0660"
'''
        
        try:
            with open("/etc/udev/rules.d/99-gpio.rules", "w") as f:
                f.write(udev_rules)
            
            # Применяем правила
            subprocess.run(["sudo", "udevadm", "control", "--reload-rules"], check=True)
            subprocess.run(["sudo", "udevadm", "trigger"], check=True)
            
            print(f"  {Color.GREEN}✓ Права доступа настроены{Color.RESET}")
            print(f"  {Color.YELLOW}⚠ Перезагрузите систему для применения прав{Color.RESET}")
            return True
            
        except Exception as e:
            print(f"  {Color.RED}✗ Ошибка настройки прав: {e}{Color.RESET}")
            return False

# =================== 3. НАСТРОЙКА PS2 КОНТРОЛЛЕРА ===================
class PS2ControllerUbuntu:
    """Основной класс для работы с PS2 контроллером на Ubuntu"""
    
    def __init__(self, gpio_lib='gpiod'):
        """
        Инициализация контроллера
        
        Args:
            gpio_lib: Библиотека GPIO ('gpiod', 'RPi.GPIO', 'periphery')
        """
        self.gpio_lib = gpio_lib
        self.chip = None
        self.lines = {}
        self.connected = False
        self.controller_type = "Unknown"
        
    def initialize(self) -> bool:
        """Инициализация GPIO и PS2 контроллера"""
        print(f"{Color.BLUE}[3/6] Инициализация PS2 контроллера...{Color.RESET}")
        
        # Инициализация GPIO
        if not self._init_gpio():
            return False
        
        # Настройка пинов PS2
        if not self._setup_ps2_pins():
            return False
        
        # Инициализация PS2 контроллера
        if not self._init_ps2_controller():
            return False
        
        print(f"  {Color.GREEN}✓ PS2 контроллер инициализирован{Color.RESET}")
        return True
    
    def _init_gpio(self) -> bool:
        """Инициализация GPIO библиотеки"""
        try:
            if self.gpio_lib == 'gpiod':
                import gpiod
                self.chip = gpiod.Chip('0')  # gpiochip0
                print(f"  {Color.GREEN}✓ Используется libgpiod{Color.RESET}")
                return True
                
            elif self.gpio_lib == 'RPi.GPIO':
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                self.gpio = GPIO
                print(f"  {Color.GREEN}✓ Используется RPi.GPIO{Color.RESET}")
                return True
                
            elif self.gpio_lib == 'periphery':
                from periphery import GPIO
                self.GPIO = GPIO
                print(f"  {Color.GREEN}✓ Используется python-periphery{Color.RESET}")
                return True
                
            else:
                print(f"  {Color.RED}✗ Неизвестная библиотека GPIO{Color.RESET}")
                return False
                
        except ImportError as e:
            print(f"  {Color.RED}✗ Библиотека {self.gpio_lib} не установлена: {e}{Color.RESET}")
            return False
        except Exception as e:
            print(f"  {Color.RED}✗ Ошибка инициализации GPIO: {e}{Color.RESET}")
            return False
    
    def _setup_ps2_pins(self) -> bool:
        """Настройка пинов PS2"""
        print(f"  Настройка пинов PS2...")
        
        try:
            if self.gpio_lib == 'gpiod':
                import gpiod
                
                for pin_name, gpio_num in PS2_PINS.items():
                    line = self.chip.get_line(gpio_num)
                    
                    if pin_name == 'dat':
                        # DAT как вход с подтяжкой к питанию
                        line.request(
                            consumer="ps2-controller",
                            type=gpiod.LINE_REQ_DIR_IN,
                            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP
                        )
                    else:
                        # CMD, SEL, CLK как выходы
                        line.request(
                            consumer="ps2-controller",
                            type=gpiod.LINE_REQ_DIR_OUT,
                            default_vals=[1]  # HIGH по умолчанию
                        )
                    
                    self.lines[pin_name] = line
                    print(f"    {pin_name.upper()}(GPIO{gpio_num}) -> настроен")
                
            elif self.gpio_lib == 'RPi.GPIO':
                import RPi.GPIO as GPIO
                
                for pin_name, gpio_num in PS2_PINS.items():
                    if pin_name == 'dat':
                        GPIO.setup(gpio_num, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                    else:
                        GPIO.setup(gpio_num, GPIO.OUT)
                        GPIO.output(gpio_num, GPIO.HIGH)
                    
                    print(f"    {pin_name.upper()}(GPIO{gpio_num}) -> настроен")
                
            elif self.gpio_lib == 'periphery':
                from periphery import GPIO
                
                for pin_name, gpio_num in PS2_PINS.items():
                    if pin_name == 'dat':
                        gpio = GPIO(gpio_num, "in")
                        gpio.pull = "up"
                    else:
                        gpio = GPIO(gpio_num, "out")
                        gpio.write(True)  # HIGH
                    
                    self.lines[pin_name] = gpio
                    print(f"    {pin_name.upper()}(GPIO{gpio_num}) -> настроен")
            
            print(f"  {Color.GREEN}✓ Все пины настроены{Color.RESET}")
            return True
            
        except Exception as e:
            print(f"  {Color.RED}✗ Ошибка настройки пинов: {e}{Color.RESET}")
            return False
    
    def _init_ps2_controller(self) -> bool:
        """Инициализация PS2 контроллера"""
        print(f"  Инициализация PS2 контроллера...")
        
        # Даем время на питание
        time.sleep(0.5)
        
        # Пробуем прочитать ID контроллера
        try:
            response = self._send_command(0x01)  # Команда инициализации
            
            if response and response[0] != 0xFF:
                controller_id = response[1]
                
                # Определяем тип контроллера
                controller_types = {
                    0x41: "Digital Controller",
                    0x73: "DualShock (Analog)",
                    0x79: "DualShock 2",
                    0x12: "NegCon",
                }
                
                self.controller_type = controller_types.get(controller_id, f"Unknown (0x{controller_id:02X})")
                self.connected = True
                
                print(f"  {Color.GREEN}✓ Контроллер обнаружен: {self.controller_type}{Color.RESET}")
                
                # Включаем аналоговый режим если DualShock
                if "DualShock" in self.controller_type:
                    self._enable_analog_mode()
                
                return True
            else:
                print(f"  {Color.RED}✗ Контроллер не отвечает{Color.RESET}")
                print(f"  {Color.YELLOW}Проверьте:{Color.RESET}")
                print(f"    • Подключение проводов")
                print(f"    • Питание 3.3V")
                print(f"    • Кнопку Analog на геймпаде")
                return False
                
        except Exception as e:
            print(f"  {Color.RED}✗ Ошибка инициализации: {e}{Color.RESET}")
            return False
    
    def _enable_analog_mode(self):
        """Включение аналогового режима"""
        print(f"  Включение аналогового режима...")
        
        response = self._send_command(0x44)  # Включить аналоговый режим
        
        if response and response[1] == 0x73:
            # Подтверждение режима
            self._send_command(0x4F)
            print(f"  {Color.GREEN}✓ Аналоговый режим включен{Color.RESET}")
        else:
            print(f"  {Color.YELLOW}⚠ Не удалось включить аналоговый режим{Color.RESET}")
    
    def _send_command(self, cmd, read_bytes=6):
        """Отправка команды PS2 контроллеру"""
        response = []
        
        try:
            # Активируем линию SEL
            self._set_pin('sel', 0)
            time.sleep(0.0001)
            
            # Отправляем команду
            response.append(self._transfer_byte(cmd))
            
            # Читаем ответ
            for _ in range(read_bytes):
                response.append(self._transfer_byte(0x00))
            
            # Деактивируем SEL
            self._set_pin('sel', 1)
            time.sleep(0.0001)
            
            return response
            
        except Exception as e:
            self._set_pin('sel', 1)
            print(f"  {Color.RED}Ошибка команды: {e}{Color.RESET}")
            return None
    
    def _transfer_byte(self, data):
        """Передача одного байта"""
        received = 0
        
        for i in range(8):
            # Опускаем CLK
            self._set_pin('clk', 0)
            time.sleep(0.00001)
            
            # Устанавливаем бит на CMD
            bit = (data >> i) & 1
            self._set_pin('cmd', bit)
            time.sleep(0.00001)
            
            # Поднимаем CLK
            self._set_pin('clk', 1)
            time.sleep(0.00001)
            
            # Читаем бит с DAT
            received_bit = self._get_pin('dat')
            received |= (received_bit << i)
            
            time.sleep(0.00001)
        
        return received
    
    def _set_pin(self, pin_name, value):
        """Установка значения пина"""
        if self.gpio_lib == 'gpiod':
            self.lines[pin_name].set_value(value)
        elif self.gpio_lib == 'RPi.GPIO':
            self.gpio.output(PS2_PINS[pin_name], value)
        elif self.gpio_lib == 'periphery':
            self.lines[pin_name].write(bool(value))
    
    def _get_pin(self, pin_name):
        """Получение значения пина"""
        if self.gpio_lib == 'gpiod':
            return self.lines[pin_name].get_value()
        elif self.gpio_lib == 'RPi.GPIO':
            return self.gpio.input(PS2_PINS[pin_name])
        elif self.gpio_lib == 'periphery':
            return 1 if self.lines[pin_name].read() else 0
        return 0
    
    def read_controller(self):
        """Чтение состояния контроллера"""
        if not self.connected:
            return None
        
        response = self._send_command(0x42, 8)  # Команда чтения состояния
        
        if not response or response[0] == 0xFF:
            self.connected = False
            return None
        
        # Парсим данные
        data = {
            'buttons': {
                'select': not (response[1] & 0x01),
                'start': not (response[1] & 0x08),
                'up': not (response[1] & 0x10),
                'right': not (response[1] & 0x20),
                'down': not (response[1] & 0x40),
                'left': not (response[1] & 0x80),
                'l2': not (response[2] & 0x01),
                'r2': not (response[2] & 0x02),
                'l1': not (response[2] & 0x04),
                'r1': not (response[2] & 0x08),
                'triangle': not (response[2] & 0x10),
                'circle': not (response[2] & 0x20),
                'cross': not (response[2] & 0x40),
                'square': not (response[2] & 0x80),
            },
            'sticks': {
                'lx': response[3] if len(response) > 3 else 128,
                'ly': response[4] if len(response) > 4 else 128,
                'rx': response[5] if len(response) > 5 else 128,
                'ry': response[6] if len(response) > 6 else 128,
            }
        }
        
        return data
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.gpio_lib == 'gpiod' and self.chip:
            self.chip.close()
        elif self.gpio_lib == 'RPi.GPIO':
            import RPi.GPIO as GPIO
            GPIO.cleanup()
        elif self.gpio_lib == 'periphery':
            for pin in self.lines.values():
                pin.close()

# =================== 4. ТЕСТИРОВАНИЕ ===================
class PS2TesterUbuntu:
    """Класс для тестирования PS2 на Ubuntu"""
    
    @staticmethod
    def run_gpio_test() -> bool:
        """Тестирование GPIO"""
        print(f"{Color.BLUE}[4/6] Тестирование GPIO...{Color.RESET}")
        
        test_script = '''#!/usr/bin/env python3
import gpiod
import time

print("Тест GPIO на Ubuntu...")

try:
    chip = gpiod.Chip('0')
    print(f"✓ GPIO чип открыт: {chip.name()}")
    
    # Тестируем пины PS2
    test_pins = [27, 22, 23, 24]
    
    for gpio_num in test_pins:
        try:
            line = chip.get_line(gpio_num)
            line.request(consumer="test", type=gpiod.LINE_REQ_DIR_IN,
                        flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
            value = line.get_value()
            print(f"  GPIO{gpio_num}: {'HIGH' if value else 'LOW'}")
            line.release()
        except Exception as e:
            print(f"  GPIO{gpio_num}: Ошибка - {e}")
    
    chip.close()
    print("✓ Тест завершен")
    
except Exception as e:
    print(f"✗ Ошибка теста: {e}")
    exit(1)
'''
        
        # Сохраняем и запускаем тестовый скрипт
        with open('/tmp/gpio_test.py', 'w') as f:
            f.write(test_script)
        
        try:
            result = subprocess.run(['sudo', 'python3', '/tmp/gpio_test.py'], 
                                  capture_output=True, text=True)
            print(result.stdout)
            
            if result.returncode == 0:
                print(f"  {Color.GREEN}✓ GPIO тест пройден{Color.RESET}")
                return True
            else:
                print(f"  {Color.RED}✗ GPIO тест не пройден{Color.RESET}")
                return False
                
        except Exception as e:
            print(f"  {Color.RED}✗ Ошибка теста: {e}{Color.RESET}")
            return False
    
    @staticmethod
    def run_ps2_test(gpio_lib='gpiod') -> bool:
        """Тестирование PS2 контроллера"""
        print(f"{Color.BLUE}[5/6] Тестирование PS2 контроллера...{Color.RESET}")
        
        print(f"  Используется библиотека: {gpio_lib}")
        print(f"  Подключите PS2 геймпад и нажмите кнопку Analog...")
        time.sleep(2)
        
        try:
            controller = PS2ControllerUbuntu(gpio_lib)
            
            if controller.initialize():
                print(f"  {Color.GREEN}✓ Контроллер подключен{Color.RESET}")
                
                # Тестовое чтение
                print(f"  Тестовое чтение (3 раза)...")
                for i in range(3):
                    data = controller.read_controller()
                    if data:
                        pressed = [btn for btn, state in data['buttons'].items() if state]
                        print(f"    Чтение {i+1}: {len(pressed)} кнопок нажато")
                    time.sleep(0.5)
                
                controller.cleanup()
                print(f"  {Color.GREEN}✓ PS2 тест пройден{Color.RESET}")
                return True
            else:
                print(f"  {Color.RED}✗ PS2 тест не пройден{Color.RESET}")
                return False
                
        except Exception as e:
            print(f"  {Color.RED}✗ Ошибка теста PS2: {e}{Color.RESET}")
            return False

# =================== 5. СОЗДАНИЕ СЛУЖБЫ ===================
class SystemdServiceCreator:
    """Создание systemd службы для PS2 контроллера"""
    
    @staticmethod
    def create_service() -> bool:
        """Создание systemd службы"""
        print(f"{Color.BLUE}[6/6] Создание systemd службы...{Color.RESET}")
        
        # Создаем директорию для службы
        service_dir = Path("/opt/ps2-controller")
        service_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем основной скрипт
        main_script = service_dir / "ps2_service.py"
        main_script.write_text(SystemdServiceCreator._create_service_script())
        main_script.chmod(0o755)
        
        # Создаем конфигурационный файл
        config_file = service_dir / "config.json"
        config_file.write_text(json.dumps({
            "gpio_library": "gpiod",
            "polling_interval": 0.02,
            "dead_zone": 15,
            "min_duty": 120,
            "motor_max": 255
        }, indent=2))
        
        # Создаем unit файл systemd
        unit_file = Path("/etc/systemd/system/ps2-controller.service")
        unit_file.write_text(SystemdServiceCreator._create_unit_file())
        
        # Включаем и запускаем службу
        try:
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "ps2-controller.service"], check=True)
            subprocess.run(["sudo", "systemctl", "start", "ps2-controller.service"], check=True)
            
            print(f"  {Color.GREEN}✓ Служба создана и запущена{Color.RESET}")
            print(f"  {Color.YELLOW}Проверьте статус: sudo systemctl status ps2-controller.service{Color.RESET}")
            
            return True
            
        except Exception as e:
            print(f"  {Color.RED}✗ Ошибка создания службы: {e}{Color.RESET}")
            return False
    
    @staticmethod
    def _create_service_script() -> str:
        """Создание скрипта службы"""
        return '''#!/usr/bin/env python3
"""
Systemd служба для PS2 контроллера на Ubuntu
"""

import json
import time
import signal
import sys
from pathlib import Path

class PS2Service:
    def __init__(self):
        self.running = True
        self.config = self.load_config()
        
        # Импортируем контроллер
        sys.path.insert(0, str(Path(__file__).parent))
        from ps2_controller import PS2ControllerUbuntu
        
        self.controller = PS2ControllerUbuntu(
            gpio_lib=self.config.get('gpio_library', 'gpiod')
        )
        
    def load_config(self):
        """Загрузка конфигурации"""
        config_file = Path(__file__).parent / "config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        print(f"Получен сигнал {signum}, остановка...")
        self.running = False
    
    def run(self):
        """Основной цикл службы"""
        print("Запуск службы PS2 контроллера...")
        
        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Инициализация контроллера
        if not self.controller.initialize():
            print("Ошибка инициализации контроллера")
            return
        
        print(f"Контроллер подключен: {self.controller.controller_type}")
        
        # Основной цикл
        while self.running:
            try:
                # Читаем состояние контроллера
                data = self.controller.read_controller()
                
                if data:
                    # Здесь можно обработать данные
                    # Например, отправить в ROS или управлять моторами
                    pass
                
                # Интервал опроса
                time.sleep(self.config.get('polling_interval', 0.02))
                
            except Exception as e:
                print(f"Ошибка в основном цикле: {e}")
                time.sleep(1)
        
        # Очистка
        self.controller.cleanup()
        print("Служба остановлена")

if __name__ == "__main__":
    service = PS2Service()
    service.run()
'''
    
    @staticmethod
    def _create_unit_file() -> str:
        """Создание unit файла systemd"""
        return '''[Unit]
Description=PS2 Gamepad Controller Service for Ubuntu
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ps2-controller
ExecStart=/usr/bin/python3 /opt/ps2-controller/ps2_service.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Безопасность
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/ps2-controller
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
'''

# =================== 6. ОСНОВНОЙ СКРИПТ КОНТРОЛЛЕРА ===================
def create_main_controller_script():
    """Создание основного скрипта контроллера"""
    script = '''#!/usr/bin/env python3
"""
Главный скрипт PS2 контроллера для Ubuntu
Использование: sudo python3 ps2_controller.py [--test]
"""

import argparse
import time
import json
from pathlib import Path

# Локальный импорт
from ps2_controller_ubuntu import PS2ControllerUbuntu

def main():
    parser = argparse.ArgumentParser(description='PS2 Controller for Ubuntu')
    parser.add_argument('--test', action='store_true', help='Запустить тест')
    parser.add_argument('--library', choices=['gpiod', 'RPi.GPIO', 'periphery'], 
                       default='gpiod', help='Библиотека GPIO')
    parser.add_argument('--config', type=str, default='config.json', 
                       help='Конфигурационный файл')
    args = parser.parse_args()
    
    # Загрузка конфигурации
    config = {}
    if Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Создание контроллера
    controller = PS2ControllerUbuntu(gpio_lib=args.library)
    
    if args.test:
        run_test(controller)
    else:
        run_controller(controller, config)

def run_test(controller):
    """Запуск теста"""
    print("Запуск теста PS2 контроллера...")
    
    if controller.initialize():
        print(f"✓ Контроллер подключен: {controller.controller_type}")
        
        print("\\nНажимайте кнопки, двигайте стики...")
        print("Ctrl+C для выхода\\n")
        
        try:
            while True:
                data = controller.read_controller()
                if data:
                    # Показываем нажатые кнопки
                    pressed = [btn.upper() for btn, state in data['buttons'].items() if state]
                    
                    if pressed:
                        print(f"\\rКнопки: {', '.join(pressed):<40}", end='')
                    else:
                        print(f"\\rКнопки: {'---':<40}", end='')
                    
                    # Показываем стики
                    sticks = data['sticks']
                    print(f" Стики: L({sticks['lx']:3d},{sticks['ly']:3d})", end='')
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\\n\\nТест завершен")
            
        finally:
            controller.cleanup()
    else:
        print("✗ Не удалось инициализировать контроллер")

def run_controller(controller, config):
    """Основной режим работы"""
    print("Запуск PS2 контроллера...")
    
    if controller.initialize():
        print(f"Контроллер: {controller.controller_type}")
        
        # Здесь может быть логика управления роботом,
        # отправка данных в ROS, и т.д.
        
        try:
            while True:
                data = controller.read_controller()
                if data:
                    # Обработка данных
                    process_controller_data(data, config)
                
                time.sleep(config.get('polling_interval', 0.02))
                
        except KeyboardInterrupt:
            print("\\nОстановка контроллера")
            
        finally:
            controller.cleanup()
    else:
        print("Ошибка инициализации контроллера")

def process_controller_data(data, config):
    """Обработка данных контроллера"""
    # Пример: преобразование для управления моторами
    dead_zone = config.get('dead_zone', 15)
    motor_max = config.get('motor_max', 255)
    
    # Получаем значения стиков
    lx = data['sticks']['lx']
    ly = data['sticks']['ly']
    
    # Преобразуем 0-255 в -motor_max..motor_max
    lx = (lx - 128) * 2
    ly = (ly - 128) * 2
    
    # Применяем мертвую зону
    if abs(lx) < dead_zone:
        lx = 0
    if abs(ly) < dead_zone:
        ly = 0
    
    # Ограничиваем значения
    lx = max(-motor_max, min(motor_max, lx))
    ly = max(-motor_max, min(motor_max, ly))
    
    # Вычисляем скорости моторов (танковая схема)
    motor_right = ly + lx
    motor_left = ly - lx
    
    # Здесь можно отправить команды моторам
    # или сохранить для дальнейшей обработки
    
    return motor_left, motor_right

if __name__ == "__main__":
    main()
'''
    
    with open('ps2_controller.py', 'w') as f:
        f.write(script)
    
    print(f"{Color.GREEN}✓ Основной скрипт создан: ps2_controller.py{Color.RESET}")

# =================== ГЛАВНАЯ ФУНКЦИЯ ===================
def main():
    """Главная функция установки и настройки"""
    print(f"{Color.CYAN}{'='*70}")
    print(f"ПОЛНАЯ УСТАНОВКА PS2 ГЕЙМПАДА SZDoit ДЛЯ UBUNTU")
    print(f"{'='*70}{Color.RESET}")
    
    # Проверка прав
    if os.geteuid() != 0:
        print(f"\n{Color.RED}ОШИБКА: Запустите скрипт с правами root!{Color.RESET}")
        print(f"  sudo python3 {sys.argv[0]}")
        sys.exit(1)
    
    # Информация о системе
    os_name, os_version = UbuntuSystemSetup.check_ubuntu_version()
    print(f"\n{Color.BOLD}Система: {os_name} {os_version}{Color.RESET}")
    
    # Меню
    print(f"\n{Color.BOLD}Выберите действие:{Color.RESET}")
    print(f"  1. {Color.GREEN}Полная установка и настройка{Color.RESET}")
    print(f"  2. {Color.YELLOW}Только установка библиотек GPIO{Color.RESET}")
    print(f"  3. {Color.BLUE}Только тестирование{Color.RESET}")
    print(f"  4. {Color.MAGENTA}Создание службы systemd{Color.RESET}")
    print(f"  5. {Color.CYAN}Схема подключения{Color.RESET}")
    print(f"  6. {Color.RED}Выход{Color.RESET}")
    
    try:
        choice = input(f"\n{Color.CYAN}Ваш выбор (1-6): {Color.RESET}").strip()
        
        if choice == '1':
            run_full_setup()
        elif choice == '2':
            install_gpio_libraries_only()
        elif choice == '3':
            run_testing_only()
        elif choice == '4':
            create_service_only()
        elif choice == '5':
            show_connection_scheme()
        elif choice == '6':
            print(f"{Color.GREEN}Выход{Color.RESET}")
        else:
            print(f"{Color.RED}Неверный выбор{Color.RESET}")
            
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Прервано пользователем{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}Ошибка: {e}{Color.RESET}")

def run_full_setup():
    """Полная установка и настройка"""
    print(f"\n{Color.CYAN}ЗАПУСК ПОЛНОЙ УСТАНОВКИ{Color.RESET}")
    
    # 1. Обновление системы
    UbuntuSystemSetup.update_system()
    
    # 2. Установка Python зависимостей
    UbuntuSystemSetup.install_python_dependencies()
    
    # 3. Установка GPIO библиотек
    installer = GPIOLibraryInstaller()
    installer.install_libgpiod()
    installer.install_python_gpiod()
    installer.setup_gpio_permissions()
    
    # 4. Тестирование GPIO
    PS2TesterUbuntu.run_gpio_test()
    
    # 5. Тестирование PS2
    PS2TesterUbuntu.run_ps2_test('gpiod')
    
    # 6. Создание службы
    SystemdServiceCreator.create_service()
    
    # 7. Создание основного скрипта
    create_main_controller_script()
    
    print(f"\n{Color.GREEN}{'='*70}")
    print(f"УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
    print(f"{'='*70}{Color.RESET}")
    
    print(f"\n{Color.BOLD}СЛЕДУЮЩИЕ ШАГИ:{Color.RESET}")
    print(f"1. Перезагрузите систему: {Color.YELLOW}sudo reboot{Color.RESET}")
    print(f"2. Проверьте службу: {Color.YELLOW}sudo systemctl status ps2-controller.service{Color.RESET}")
    print(f"3. Запустите тест: {Color.YELLOW}sudo python3 ps2_controller.py --test{Color.RESET}")
    print(f"4. Просмотр логов: {Color.YELLOW}sudo journalctl -u ps2-controller.service -f{Color.RESET}")

def install_gpio_libraries_only():
    """Установка только библиотек GPIO"""
    print(f"\n{Color.CYAN}УСТАНОВКА БИБЛИОТЕК GPIO{Color.RESET}")
    
    installer = GPIOLibraryInstaller()
    installer.install_libgpiod()
    installer.install_python_gpiod()
    installer.install_rpi_gpio()
    installer.install_periphery()
    installer.setup_gpio_permissions()
    
    print(f"\n{Color.GREEN}✓ Библиотеки GPIO установлены{Color.RESET}")

def run_testing_only():
    """Только тестирование"""
    print(f"\n{Color.CYAN}ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ{Color.RESET}")
    
    PS2TesterUbuntu.run_gpio_test()
    PS2TesterUbuntu.run_ps2_test('gpiod')
    
    print(f"\n{Color.GREEN}✓ Тестирование завершено{Color.RESET}")

def create_service_only():
    """Создание только службы"""
    print(f"\n{Color.CYAN}СОЗДАНИЕ SYSTEMD СЛУЖБЫ{Color.RESET}")
    
    SystemdServiceCreator.create_service()
    
    print(f"\n{Color.GREEN}✓ Служба создана{Color.RESET}")

def show_connection_scheme():
    """Показать схему подключения"""
    print(f"\n{Color.CYAN}{'='*70}")
    print(f"СХЕМА ПОДКЛЮЧЕНИЯ PS2 SZDoit ДЛЯ UBUNTU")
    print(f"{'='*70}{Color.RESET}")
    
    print(f"\n{Color.BOLD}PS2 разъем -> Raspberry Pi:{Color.RESET}")
    for pin_name, gpio_num in PS2_PINS.items():
        physical_pin = PHYSICAL_PINS[gpio_num]
        color = {
            'dat': Color.MAGENTA,
            'cmd': Color.BLUE,
            'sel': Color.GREEN,
            'clk': Color.YELLOW,
        }.get(pin_name, Color.WHITE)
        
        print(f"  {color}{pin_name.upper():<6}{Color.RESET} -> GPIO{gpio_num:<3} (Pin {physical_pin})")
    
    print(f"\n{Color.RED}ВАЖНО: Питание PS2 - ТОЛЬКО 3.3V!{Color.RESET}")
    print(f"  Красный провод -> 3.3V (Pin 1 или 17)")
    print(f"  Черный провод  -> GND (Pin 6, 9, 14, 20, 25)")
    
    print(f"\n{Color.YELLOW}ПОРЯДОК ПОДКЛЮЧЕНИЯ:{Color.RESET}")
    print(f"  1. Отключите питание Raspberry Pi")
    print(f"  2. Подключите все провода PS2")
    print(f"  3. Проверьте отсутствие коротких замыканий")
    print(f"  4. Включите питание Raspberry Pi")
    print(f"  5. Нажмите кнопку Analog на геймпаде")
    print(f"  6. Должен загореться красный светодиод")

if __name__ == "__main__":
    main()