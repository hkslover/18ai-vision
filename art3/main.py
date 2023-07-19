import sensor
import struct
from machine import UART
import math
# y_dict = {21:104-5,20:81-4,19:68-2,18:61-1,17:53-1,16:50-1,15:48-1,14:40,13:37,12:34}
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_brightness(450)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.skip_frames(time = 500)
uart = UART(2, baudrate=115200)
detect_flag = 0
task_id = 0
def pack_data(xoffset,yoffset):
    data = bytearray()
    data += struct.pack('!HH', xoffset, yoffset)
    data_len = len(data) + 1
    header = bytearray([0xAA, data_len, 0x03])
    checksum = 0 ^ 0x01
    for byte in data:
        checksum ^= byte
    footer = bytearray([checksum, 0x55])
    #print(header + data + footer)
    return header + data + footer

def no_card_pack_data():
    data = bytearray()
    data += struct.pack('!BBBB', 255,255,255,255)
    data_len = len(data) + 1
    header = bytearray([0xAA, data_len, 0xFF])
    checksum = 0 ^ 0xFF
    for byte in data:
        checksum ^= byte
    footer = bytearray([checksum, 0x55])
    return header + data + footer
x_offsets = 149
y_offsets = 234
all_obj_list = []
show_obj_list = []
blue_thresholds = [(0, 100, -8, 79, -111, -10)]
#blue_thresholds = [(0, 100, -128, 127, -113, 2)]
send_times = 0
missing_times = 0
set_roi = (25,45,269,240 - 45)
M = [-8.81927711000000,-33.2048193000000,1646.33735000000,-1.12079145000000e-12,-68.9638554000000,2221.59036000000,-4.44408361000000e-15,-0.240963855000000,1]
while True:
    detect_flag = 0
    img = sensor.snapshot()
    if(uart.any()):
        task_id = uart.readchar()
    #img.draw_line(0,45,320,45,color = (0,0,255))
    #img.draw_line(0,50,320,50,color = (0,0,255))
    #img.draw_line(269,50,269,240,color = (0,0,255)) # roi = (0,50,269,190),
    if(task_id == 0):
        set_roi = (25,45,269,240 - 45)
    elif(task_id == 1):
        set_roi = (25,15,269,240 - 15)
    #img.draw_rectangle(set_roi,color = (0,0,255))
    blobs = img.find_blobs(blue_thresholds,roi = set_roi,invert=True,merge=False)
    for blob in blobs:
        area = blob.area()
        w = blob.w()
        h = blob.h()
        x = blob.x()
        y = blob.y()
        if area > 2500 or area < 20:
            continue
        if w < h:
            continue
        if w > 100:
            continue
        #if p > 4 or p < 2.5:
            #continue
        x2 = x + w
        y2 = y
        x3 = x
        y3 = y + h

        denom = M[6] * x + M[7] * y + 1
        x_transformed = (M[0] * x + M[1] * y + M[2]) / denom
        y_transformed = (M[3] * x + M[4] * y + M[5]) / denom

        denom = M[6] * x2 + M[7] * y2 + 1
        x2_transformed = (M[0] * x2 + M[1] * y2 + M[2]) / denom
        y2_transformed = (M[3] * x2 + M[4] * y2 + M[5]) / denom

        denom = M[6] * x3 + M[7] * y3 + 1
        x3_transformed = (M[0] * x3 + M[1] * y3 + M[2]) / denom
        y3_transformed = (M[3] * x3 + M[4] * y3 + M[5]) / denom
        #print(x2_transformed - x_transformed,y3_transformed-y_transformed)
        if (abs(abs(x2_transformed - x_transformed) - abs(y3_transformed-y_transformed)) > 30):
            #img.draw_rectangle(blob.rect(),color = (255,0,0))
            #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h(),str("1"))
            continue
        elif(abs(x2_transformed - x_transformed) < 10):
            #img.draw_rectangle(blob.rect(),color = (255,0,0))
            #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h(),str("2"))
            continue
        elif(abs(x2_transformed - x_transformed) > 20):
            #img.draw_rectangle(blob.rect(),color = (255,0,0))
            #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h(),str("3"))
            continue
        elif(abs(y3_transformed - y_transformed) < 11):
            #img.draw_rectangle(blob.rect(),color = (255,0,0))
            #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h(),str("3"))
            continue
        elif(abs(y3_transformed - y_transformed) > 19):
            #img.draw_rectangle(blob.rect(),color = (255,0,0))
            #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h(),str("3"))
            continue
        if(y < 50):
            if(blob.pixels()/area < 0.65):
                #img.draw_rectangle(blob.rect(),color = (255,0,0))
                #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h(),str("4"))
                continue
        else:
            if(blob.pixels()/area < 0.3):
                #img.draw_rectangle(blob.rect(),color = (255,0,0))
                #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h(),str("4"))
                continue
        #y < 80 0.75  blob.pixels()/area以上
        #print(x_transformed,y_transformed)
        #(x_transformed + x2_transformed) // 2

        all_obj_list.append(((x_transformed + x2_transformed) // 2 - x_offsets,(y3_transformed + y_transformed) // 2  - y_offsets))
        show_obj_list.append((x,y,w,h))
        #print(show_obj_list)
        # _px = -(int((x_transformed + x2_transformed) // 2 - 149))
        # _py = -(int((y3_transformed+y_transformed) // 2 - 234))
        # uart.write(pack_data(_px,_py))
        # detect_flag = 1
        # print(-((x_transformed + x2_transformed) // 2 - 149),-((y3_transformed+y_transformed) // 2 - 234))
        #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h()+5,str(abs(blob.pixels()/area)))
        #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h()+5,str(blob.h()))
        #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h()+10,str(blob.area()))
        #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h()+16,str(blob.pixels()/area))
        #img.draw_string(blob.x()+blob.w(),blob.y()+blob.h()+40,str(abs(abs(x2_transformed - x_transformed) - abs(y3_transformed-y_transformed))))
        # img.draw_rectangle(blob.rect(),color = (0,255,0))
        #print(pre_h,h)
    # if detect_flag != 1:
        #print(no_card_pack_data())
        # uart.write(no_card_pack_data())
    #frame_times += 1
    #and frame_times == 3
    if(len(show_obj_list) != 0):
        #frame_times = 0
        if(len(show_obj_list) == 1):
            nearest_obj_index = 0
        else:
            nearest_obj_index = max(range(len(show_obj_list)), key=lambda i: show_obj_list[i][2])
        #i = 0
        #nearest_obj_index = 0
        #min_distance = 9999
        #for obj in show_obj_list:
            #distance = math.pow(int(obj[0]) - 160,2) + math.pow(int(obj[1]) - 240,2)
            #if(distance < min_distance):
                #min_distance = min_distance
                #nearest_obj_index = i
            #i = i + 1
        if(send_times != 2):
            send_times += 1
        else:
            send_times = 0
            uart.write(pack_data(int(all_obj_list[nearest_obj_index][0]),int(all_obj_list[nearest_obj_index][1])))
            print(show_obj_list[nearest_obj_index][1])
            img.draw_rectangle(show_obj_list[nearest_obj_index],color = (0,255,0))
        #print('success')
    else:
        missing_times += 1
        if(missing_times == 5):
            print(no_card_pack_data())
            uart.write(no_card_pack_data())
            missing_times = 0
    all_obj_list.clear()
    show_obj_list.clear()
