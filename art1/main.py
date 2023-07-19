import struct
from machine import UART
import sensor
import math
import pyb
import tf
from uart_data_pack import pack_data
#task_id = 0
uart = UART(2,baudrate=115200)
data_list = []
# 数据集拍摄
label_list = ['chili', 'orange', 'radish', 'apple', 'eggplant', 'durian', 'cabbage', 'peanut', 'bean', 'cucumber', 'corn', 'grape', 'banana', 'rice', 'potato']
label_dict = {0: 'chili', 1: 'orange', 2: 'radish', 3: 'apple', 4: 'eggplant', 5: 'durian', 6: 'cabbage', 7: 'peanut', 8: 'bean', 9: 'cucumber', 10: 'corn', 11: 'grape', 12: 'banana', 13: 'rice', 14: 'potato'}
labels = ['apple','banana','bean','cabbage','chill','corn', 'cucumber', 'durian', 'eggplant', 'grape', 'orange', 'peanut', 'potato', 'radish', 'rice']

#A4纸识别变量
img_size = (320,240)

points_threshold = (35, 72, -23, 127, -64, 127) # yes
#points_threshold = (35, 100, -128, 75, -128, 127) # yes
#points_threshold = (38, 100, -128, 127, -128, 127)
a4_threshold = (39, 100, -128, 127, -128, 127)
net = tf.load('/sd/models/best.tflite', load_to_fb=True)
a4_sendtimes = 0
#识别
times = 0
def pack_data_points(points):
    data = bytearray()
    for point in points:
        data += struct.pack('!BB', point[0], point[1])
    data_len = len(data) + 1  # 1 byte for type
    header = bytearray([0xAA, data_len, 0x00])
    checksum = 0 ^ 0x00
    for byte in data:
        checksum ^= byte
    footer = bytearray([checksum, 0x55])
    return header + data + footer
def dis_point_to_line(line_param_list, Point):
    a,b,c = line_param_list
    numerator = abs((a*Point[0] + b*Point[1] + c))
    denominator = math.sqrt(pow(a, 2) + pow(b, 2))
    if denominator == 0:
        d = 0
    else:
        d = numerator/denominator
    return d
def linear_equation(Point1, Point2):
    a = Point2[1] - Point1[1]
    b = Point1[0] - Point2[0]
    c = (Point2[0] - Point1[0])*Point1[1] - (Point2[1] - Point1[1])*Point1[0]
    return [a, b, c]
def twopoints_dis(Point1, Point2):
    dis2 = pow((Point1[0]-Point2[0]),2) + pow((Point1[1]-Point2[1]),2)
    dis = math.sqrt(dis2)
    return dis
def assret_roi(roi,img_size) -> bool:
    if roi[0] > img_size[0] or roi[0] > img_size[1] \
       or roi[2] < 0 or roi[3] < 0 \
       or roi[0] + roi[2] > img_size[0] or roi[1] + roi[3] > img_size[1]:
        return False
    return True
img_list = []
blue_thresholds = [(0, 100, -8, 79, -111, -10)]
#blue_thresholds = [(0, 100, -128, 127, -113, 2)]
def find_object(img):
    blobs = img.find_blobs(blue_thresholds,invert=True,merge=True,margin=2)
    for blob in blobs:
        if abs(blob.h() - blob.w()) > 25 or blob.area() < 5300 or blob.area() > 14000 or blob.pixels()/(blob.w()*blob.h()) < 0.50:
            continue
        else:
            return blob.rect()
def find_image():
    img = sensor.snapshot()
    find_flag = 0
    blobs = img.find_blobs(blue_thresholds,invert=True,merge=True,margin=2)
    for blob in blobs:
        if abs(blob.h() - blob.w()) > 25 or blob.area() < 5300 or blob.area() > 14000 or blob.pixels()/(blob.w()*blob.h()) < 0.40:
            continue
        find_flag = 1
        obj_img = img.copy(roi=blob.rect())
        return find_flag,obj_img
    return 0,0
white_light.off()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_brightness(450)
sensor.skip_frames(time = 100)
#sensor.set_auto_gain(True)
#sensor.set_auto_whitebal(True)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

task_id = 0x01


while True:

    if(uart.any()):
        task_id = uart.readchar()
    # 数据集采集
    if(task_id == int(0x04)):
        data_len = uart.any()
        for _ in range(data_len):
            data_list.append(uart.readchar())
            print(uart.readchar())
        if data_list:
            label = label_dict[data_list[0]]
            blob_rect = find_object(img)
            if blob_rect:
                try:
                    img.save('/sd/data1/{0}/{1}.jpg'.format(label,pyb.rng()),roi=blob_rect)
                    data = pack_data(1,'保存成功 {}'.format(label))
                    uart.write(data)
                except:
                        data = pack_data(1,'保存失败 {}'.format(label))
                        uart.write(data)
            else:
                data = pack_data(1,'没有发现目标板 {}'.format(label))
                uart.write(data)
            task_id = 0
            data_list = []
    elif(task_id == int(0x01)):
        img = sensor.snapshot()
        for a4_rect in img.find_blobs([a4_threshold], pixels_threshold=1000, area_threshold=1000, merge=True, margin=10):
            #for r in img.find_rects(threshold = 8000):
            #print(a4_rect.w(),a4_rect.h())
            if(a4_rect.w() < 150 or a4_rect.h() < 100):
                continue
            #img.draw_rectangle(a4_rect.rect(), color = (255, 0, 0))
            rects = img.find_rects(roi = a4_rect.rect(),threshold=7000)
            for map_rect in rects:
                #if(map_rect.w() < 110 or map_rect.h() < 60):
                    #continue
                if(map_rect.w() < 100 or map_rect.h() < 80):
                    continue
                #img.draw_rectangle(map_rect.rect(), color = (0, 0, 255))
                a4_corners = list(map_rect.corners())
                a4_corners = sorted(a4_corners, key = lambda k: k[0])
                A_and_C = sorted(a4_corners[:2], key = lambda k: k[1])
                B_and_D = sorted(a4_corners[2:], key = lambda k: k[1])
                img.draw_cross(A_and_C[1], color=(153, 20, 80))
                A,C = A_and_C[0],A_and_C[1]
                B,D = B_and_D[0],B_and_D[1]
                AB_dis = twopoints_dis(A, B)
                CD_dis = twopoints_dis(C, D)
                AC_dis = twopoints_dis(A, C)
                BD_dis = twopoints_dis(B, D)
                CD_line_paramlist = linear_equation(C, D)
                AC_line_paramlist = linear_equation(A, C)
                mean_AB_CD = (AB_dis + CD_dis)/2
                mean_AC_BD = (AC_dis + BD_dis)/2

                x_ratio = mean_AB_CD / (36*2)
                y_ratio = mean_AC_BD / (25*2)
                #y_ratio = mean_AC_BD / (26*2)
                # points_roi = (map_rect.x()+4,map_rect.y()+2,map_rect.w()-6,map_rect.h()-4) # success
                points_roi = (map_rect.x()+4,map_rect.y()+2,map_rect.w()-9,map_rect.h()-5)
                #img.draw_rectangle(points_roi, color=(0, 255, 0))
                #for c in img.find_circles(roi =points_roi,threshold = 1400, x_margin = 1, y_margin = 1, r_margin = 1,r_min = 1, r_max =4, r_step = 1):
                    #img.draw_circle(c.x(), c.y(),2, color = (0, 0, 255),thickness = 2)
                #img.erode(1,thresold=7)
                points_list = []
                point_blobs = img.find_blobs([points_threshold], roi = points_roi,x_stride=1, y_stride=1,invert = True)
                for point_blob in point_blobs:
                    if point_blob.w() > 7 or point_blob.h() > 7:
                        continue
                    img.draw_rectangle(point_blob.rect(), color=(255, 0, 0))
                    point = (point_blob.cxf(),point_blob.cyf())
                    delta_x = dis_point_to_line(AC_line_paramlist, point)
                    delta_y = dis_point_to_line(CD_line_paramlist, point)

                    real_x = round((delta_x / x_ratio) + 1.0) // 2 # 几个半格
                    real_y = round((delta_y / y_ratio) + 1.0) // 2 # 几个半格
                    points_list.append((real_x,real_y))
                #A_C_rect = (C[0] - 5,C[1] - int(AC_dis),12,int(AC_dis))
                # img.draw_rectangle((C[0] - 5,C[1] - int(AC_dis),12,int(AC_dis)),color=(0, 0, 255))
                #for c in img.find_circles(roi = A_C_rect,threshold = 1600, x_margin = 1, y_margin = 1, r_margin = 1,r_min = 1, r_max =3, r_step = 1):
                    #img.draw_circle(c.x(), c.y(),2, color = (0, 0, 255),thickness = 2)
                if(len(points_list) == 12 or len(points_list) == 16):
                    print(points_list)
                    uart_data = pack_data(0,points_list)
                    a4_sendtimes += 1
                    uart.write(uart_data)
                #if(a4_sendtimes == 25):
                    #sensor.reset()
                    #sensor.set_pixformat(sensor.RGB565)
                    #sensor.set_framesize(sensor.QVGA)
                    #sensor.set_brightness(600)
                    #sensor.set_auto_gain(False)
                    #sensor.set_auto_whitebal(False)
                    #sensor.skip_frames(time = 20)
                    #task_id = int(0x00)
    elif(task_id == int(0x02)):
        while(len(img_list) != 5):
            find_flag, obj_img = find_image()
            if(find_flag):
                img_list.append(obj_img)
        if(len(img_list) == 5):
            result_dict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0}
            for i in range(5):
                scores = tf.classify(net,img_list[i])[0].output()
                max_score = max(scores)
                max_label_index = scores.index(max_score)
                result_dict[max_label_index] += 1
                print(labels[max_label_index])
            #print(max(result_dict,key=result_dict.get))
            #img_list[4].save('/sd/data8/' + str(pyb.rng()) + '.bmp')
            img_list.clear()
            uart_data = pack_data(2,max(result_dict,key=result_dict.get))
            uart.write(uart_data)
            print(uart_data)
            #img_list[0].save('/sd/data1/' + str(pyb.rng()) + '.bmp')
            task_id = int(0x00)
    elif(task_id == int(0x00)):
        pass
