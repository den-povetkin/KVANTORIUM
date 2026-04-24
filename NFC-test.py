import smbus
import time

I2C_ADDR = 0x24
bus = smbus.SMBus(1)
'''
import Adafruit_PN532 as PN532

pn532 = PN532.PN532(i2c=True, i2c_address=0x24, i2c_busnum=1)
pn532.begin()
'''

def read_pn532():
    try:
        data = bus.read_i2c_block_data(I2C_ADDR, 0, 16)
        print("Данные:", [f"0x{b:02X}" for b in data])
    except:
        print("Не удалось прочитать данные — проверьте подключение")

while True:
    read_pn532()
    time.sleep(1)
