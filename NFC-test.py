import time
import Adafruit_PN532 as PN532

# Настройка по SPI
CS   = 8
MOSI = 10
MISO = 9
SCLK = 11

pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
pn532.begin()
ic, ver, rev, support = pn532.get_firmware_version()
print(f'Найден чип PN532: версия {ver}.{rev}')

pn532.SAM_configuration()

print('Ожидание NFC-метки...')
while True:
    uid = pn532.read_passive_target()
    if uid is None:
        continue
    print(f'Найдена метка с UID: {"".join(f"{i:02X}" for i in uid)}')
    time.sleep(1)
