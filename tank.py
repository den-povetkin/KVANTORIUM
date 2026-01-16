# мин. сигнал, при котором мотор начинает вращение
MIN_DUTY = 120

# пины драйвера
MOT_RA = 2
MOT_RB = 3
MOT_LA = 4
MOT_LB = 5

# пины ресивера ps2 (используем аналоговые пины как цифровые)
PS2_DAT = 26  # A0 для ESP32
PS2_CMD = 27  # A1
PS2_SEL = 28  # A2
PS2_CLK = 29  # A3

# ===========================
#from machine import Pin, PWM, Timer
import time
import ps2controller  # Библиотеку нужно установить отдельно

# Класс для плавного управления мотором
class GMotor:
    def __init__(self, pinA, pinB, reverse=False):
        self.pwmA = PWM(Pin(pinA), freq=1000, duty=0)
        self.pwmB = PWM(Pin(pinB), freq=1000, duty=0)
        self.reverse = reverse
        self.target_speed = 0
        self.current_speed = 0
        self.smooth_factor = 80  # 0-100, чем больше - тем плавнее
        
    def set_speed(self, speed):
        """Установка скорости (-255..255)"""
        if speed > 255:
            speed = 255
        elif speed < -255:
            speed = -255
            
        self.target_speed = speed
        
    def smooth_tick(self):
        """Плавное изменение скорости (вызывать в цикле)"""
        if abs(self.target_speed - self.current_speed) < 1:
            self.current_speed = self.target_speed
        else:
            # Интерполяция для плавности
            diff = self.target_speed - self.current_speed
            self.current_speed += diff * (self.smooth_factor / 100)
            
        self._apply_speed()
        
    def _apply_speed(self):
        """Применение текущей скорости к моторам"""
        speed = self.current_speed
        
        if self.reverse:
            speed = -speed
            
        # Учет минимального сигнала
        if abs(speed) > 0 and abs(speed) < MIN_DUTY:
            speed = MIN_DUTY if speed > 0 else -MIN_DUTY
            
        duty = int(abs(speed) * 1023 / 255)  # Преобразование в диапазон PWM
        
        if speed > 0:
            self.pwmA.duty(duty)
            self.pwmB.duty(0)
        elif speed < 0:
            self.pwmA.duty(0)
            self.pwmB.duty(duty)
        else:
            self.pwmA.duty(0)
            self.pwmB.duty(0)
            
    def set_smoothness(self, factor):
        """Установка плавности (0-100)"""
        self.smooth_factor = max(0, min(100, factor))
        
    def stop(self):
        """Мгновенная остановка"""
        self.target_speed = 0
        self.current_speed = 0
        self.pwmA.duty(0)
        self.pwmB.duty(0)

# Инициализация моторов
motorR = GMotor(MOT_RA, MOT_RB, reverse=True)  # Правый мотор в обратную сторону
motorL = GMotor(MOT_LA, MOT_LB, reverse=False)  # Левый мотор нормально

# Установка плавности
motorR.set_smoothness(80)
motorL.set_smoothness(80)

# Инициализация PS2 контроллера
try:
    ps2 = ps2controller.PS2Controller(PS2_DAT, PS2_CMD, PS2_SEL, PS2_CLK)
    print("PS2 контроллер подключен")
except Exception as e:
    print("Ошибка подключения PS2:", e)
    ps2 = None

# Таймер для плавного управления моторами
def motor_tick(timer):
    motorR.smooth_tick()
    motorL.smooth_tick()

# Запуск таймера каждые 20 мс (50 Гц)
timer = Timer(-1)
timer.init(period=20, mode=Timer.PERIODIC, callback=motor_tick)

def map_value(x, in_min, in_max, out_min, out_max):
    """Аналог функции map из Arduino"""
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def constrain(value, min_val, max_val):
    """Ограничение значения"""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value

def main_loop():
    """Основной цикл управления"""
    last_check = time.ticks_ms()
    
    while True:
        current_time = time.ticks_ms()
        
        # Проверяем геймпад каждые 50 мс
        if time.ticks_diff(current_time, last_check) >= 50:
            last_check = current_time
            
            if ps2:
                try:
                    # Чтение данных с геймпада
                    ps2.read()
                    
                    if ps2.connected:
                        # Чтение аналоговых стиков (0-255)
                        lx_raw = ps2.joystick_left_x
                        ly_raw = ps2.joystick_left_y
                        
                        # Преобразуем стики от 0..255 к -255..255
                        LX = map_value(lx_raw, 255, 0, -255, 255)
                        LY = map_value(ly_raw, 255, 0, -255, 255)
                        
                        # Мертвая зона для устранения дрейфа
                        DEAD_ZONE = 15
                        if abs(LX) < DEAD_ZONE:
                            LX = 0
                        if abs(LY) < DEAD_ZONE:
                            LY = 0
                        
                        # Танковая схема управления
                        dutyR = LY + LX
                        dutyL = LY - LX
                        
                        # Ограничиваем значения
                        dutyR = constrain(dutyR, -255, 255)
                        dutyL = constrain(dutyL, -255, 255)
                        
                        # Задаем целевую скорость
                        motorR.set_speed(dutyR)
                        motorL.set_speed(dutyL)
                        
                        # Проверка кнопки экстренной остановки (SELECT)
                        if ps2.button_select:
                            print("Экстренная остановка!")
                            motorR.stop()
                            motorL.stop()
                            # Ждем отпускания кнопки
                            while ps2.button_select:
                                ps2.read()
                                time.sleep(0.01)
                    
                    else:
                        # Нет связи с геймпадом - остановка
                        print("Нет связи с геймпадом")
                        motorR.set_speed(0)
                        motorL.set_speed(0)
                        
                except Exception as e:
                    print("Ошибка чтения геймпада:", e)
                    motorR.set_speed(0)
                    motorL.set_speed(0)
            else:
                # Нет подключенного геймпада
                motorR.set_speed(0)
                motorL.set_speed(0)
        
        # Небольшая задержка для снижения нагрузки на CPU
        time.sleep_ms(10)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Остановка...")
        motorR.stop()
        motorL.stop()
        timer.deinit()