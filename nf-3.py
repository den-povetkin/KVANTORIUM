import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time

# Инициализация I2C
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Настройка PN532
pn532.SAM_configuration()

print("Ожидание NFC метки...")
print("Поднесите карту к считывателю")

while True:
    # Проверка наличия карты
    uid = pn532.read_passive_target(timeout=0.5)
    
    if uid is not None:
        print("Найдена карта с UID:", [hex(i) for i in uid])
        
        # Обработка разных типов карт
        try:
            # Для Mifare Classic
            if len(uid) == 4:
                print("Тип: Mifare Classic")
                print("Чтение блока данных...")
                
                # Аутентификация и чтение блока
                key = b'\xFF\xFF\xFF\xFF\xFF\xFF'  # ключ по умолчанию
                authenticated = pn532.mifare_classic_authenticate_block(
                    uid, 4, pn532.MIFARE_CMD_AUTH_A, key)
                
                if authenticated:
                    data = pn532.mifare_classic_read_block(4)
                    print(f"Данные блока 4: {data.hex()}")
                    
                    # Пример записи данных
                    # new_data = b'Hello Raspberry!'
                    # if len(new_data) <= 16:
                    #     pn532.mifare_classic_write_block(4, new_data.ljust(16, b'\x00'))
                    
            # Для NTAG
            elif len(uid) == 7:
                print("Тип: NTAG")
                # Чтение текста из нескольких страниц NTAG
                text_data = b''
                page_index = 4  # Начинаем чтение с 4-й страницы
                
                # Читаем несколько страниц для получения полного текста
                for i in range(8):  # Читаем 8 страниц (32 байта)
                    try:
                        page_data = pn532.ntag2xx_read_block(page_index + i)
                        if page_data is not None:
                            # Проверяем, содержит ли страница данные окончания текста
                            if b'\x00\x00' in page_data or page_data == b'\x00' * 4:
                                # Добавляем данные до первого нулевого байта
                                for j, byte in enumerate(page_data):
                                    if byte == 0:
                                        text_data += page_data[:j]
                                        break
                                else:
                                    text_data += page_data
                                break
                            text_data += page_data
                            print(f"Данные страницы {page_index + i}: {page_data.hex()}")
                        else:
                            break
                    except Exception as e:
                        print(f"Ошибка чтения страницы {page_index + i}: {e}")
                        break
                
                # Пытаемся декодировать текст
                try:
                    # Удаляем пустые байты в конце и декодируем
                    text = text_data.rstrip(b'\x00').decode('utf-8', errors='ignore')
                    if text:
                        print(f"Текст с метки: {text}")
                    else:
                        print(f"Данные в виде hex: {text_data.hex()}")
                except Exception as e:
                    print(f"Ошибка декодирования текста: {e}")
                    print(f"Данные в виде hex: {text_data.hex()}")
                
        except Exception as e:
            print(f"Ошибка: {e}")
        
        time.sleep(2)  # Задержка перед следующим чтением