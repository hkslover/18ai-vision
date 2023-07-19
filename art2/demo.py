import struct
from machine import UART
import sensor
import math

yellow = [(63, 100, -37, 29, 34, 127)]
img_size = (320,240)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_brightness(450)
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False)
sensor.skip_frames(time = 2000)

def pack_data(xoffset,yoffset):
    data = bytearray()
    data += struct.pack('!HH', xoffset, yoffset)
    data_len = len(data) + 1  # 1 byte for type
    header = bytearray([0xAA, data_len, 0x01])
    checksum = 0 ^ 0x01
    for byte in data:
        checksum ^= byte
    footer = bytearray([checksum, 0x55])
    return header + data + footer


roi = (0,20,320,240-20)
while True:
    img = sensor.snapshot()
    img.draw_line(0,20,320,20,color = (0,0,255))
    blobs = img.find_blobs(yellow,merge=True,margin=3,roi = roi)
    for blob in blobs:
        area = blob.area()
        w = blob.w()
        h = blob.h()
        _y = blob.y() + h//2
        _x = blob.x() + w//2
        if(area < 6500):
            continue
        dx = int(float(_x-148)*1.5)
        dy = int(-float(_y-175)*1.5)
        if(h > w):
            print(pack_data(dx,0))
        else:
            print(pack_data(0,dy))
        #img.draw_string(blob.x(),blob.y()-10,str(area))
        #img.draw_string(blob.x(),blob.y()-20,str(w))
        img.draw_rectangle(blob.rect(), color=(0, 255, 0))
