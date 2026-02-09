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

my_dict = {'A1': ['0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x1'],
        'A2': ['0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x2'],
        'A3': ['0x4f', '0xec', '0x86', '0xbf']
        }
cid = ''
while True:
    # Проверка наличия карты
    uid = pn532.read_passive_target(timeout=0.5)
    
    if uid is not None:
        cid=[hex(i) for i in uid]
        cidx=str(cid[0])
        cidy=str(cid[1])

        #cid = cid.replace("x", ".")
        print('Текущая координата', cidx[2],cidy[2])

        #print("Найдена карта с UID:", [hex(i) for i in uid])
    
'''    
    if uid is not None:
        print("Найдена карта с UID:", [hex(i) for i in uid])
              
        for key, value in my_dict.items():
            if value == [hex(i) for i in uid]:
                cid=[hex(i) for i in uid]
                print(cid[0])
                
                break
            else:
                print('NO')
'''                
     
    

        
'''        
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
                # Чтение страниц NTAG
                page_data = pn532.ntag2xx_read_block(4)
                print(f"Данные страницы 4: {page_data.hex()}")
                
        except Exception as e:
            print(f"Ошибка: {e}")
 '''       
#        time.sleep(2)  # Задержка перед следующим чтением
