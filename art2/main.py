import struct
from machine import UART
import sensor
import math
task_id = 0 #空闲
uart = UART(2,baudrate=115200)
data_list = []

img_size = (320,240)

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
def no_card_pack_data():
    data = bytearray()
    data += struct.pack('!BBBB', 255,255,255,255)
    data_len = len(data) + 1  # 1 byte for type
    header = bytearray([0xAA, data_len, 0xFF])
    checksum = 0 ^ 0xFF
    for byte in data:
        checksum ^= byte
    footer = bytearray([checksum, 0x55])
    return header + data + footer
blue_thresholds = [(0, 100, -8, 79, -111, -15)]
blue_thresholds = [(0, 100, -128, 127, -59, -1)]
blue_thresholds = [(0, 100, -128, 127, -128, -3)]
#blue_thresholds = [(0, 100, -128, 127, -113, 2)]
yellow_thresholds = [(63, 100, -37, 29, 34, 127)]
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_brightness(450)
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False)
sensor.skip_frames(time = 2000)

task_id = 0x01
detect_flag = 0
send_flag = 0
while True:
    img = sensor.snapshot()
    #if(uart.any()):
        #task_id = uart.readchar()
    # 目标板矫正
    if(task_id == int(0x01)):
        detect_flag = 0
        blobs = img.find_blobs(blue_thresholds,invert=True,merge=True,margin=3)
        for blob in blobs:
            if(blob.pixels()/(blob.w()*blob.h()) < 0.4 or blob.area() < 1300 or blob.w() > 110 or blob.h() > 110 or blob.w() < 35 or blob.h() < 30 or blob.area() > 12000):
               continue
            #print(blob.area(), blob.w()*blob.h() )
            blob_rect = blob.rect()
            _x = blob.x() + blob.w()//2
            _y = blob.y() + blob.h()//2
            _px = int(float(_x-148)*1.5)
            _py = int(-float(_y-175)*1.5)
            #print(pack_data(_px,_py))
            if send_flag == 5:
                uart.write(pack_data(_px,_py))
                send_flag = 0
            else:
                send_flag += 1
            detect_flag = 1
            img.draw_circle(_x, _y, 5, color=(255, 0, 255))
            img.draw_cross(_x, _y, 5, color=(255, 255, 255))
            img.draw_circle(blob.x(), blob.y(), 5, color=(255, 0, 255))
            img.draw_cross(blob.x(), blob.y(), 5, color=(255, 255, 255))
            print(_px,_py)
        if detect_flag != 1:
            print(no_card_pack_data())
            uart.write(no_card_pack_data())
        # task_id = int(0x00)
    elif(task_id == int(0x02)):
        blobs = img.find_blobs(yellow,merge=True,margin=3,roi = (0,20,320,240-20))
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
        task_id = int(0x00)
    elif(task_id == int(0x00)):
        pass
