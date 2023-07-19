import struct
from machine import UART
import sensor
import pyb
import tf
from uart_data_pack import pack_data

uart = UART(2,baudrate=256000)
data_list = []


labels = ['apple','banana','bean','cabbage','chili','corn', 'cucumber', 'durian', 'eggplant', 'grape', 'orange', 'peanut', 'potato', 'radish', 'rice']
blue_thresholds = [(0, 100, -8, 79, -111, -10)]
net = tf.load('/sd/models/best.tflite', load_to_fb=True) # best best
#net = tf.load('/sd/models/7_4_98.8.tflite', load_to_fb=True) # yes

#net = tf.load('/sd/models/7_8_best_batch200epoch32.tflite', load_to_fb=True)

#net = tf.load('/sd/models/7_8_batch200epoch31_97.tflite', load_to_fb=True) # best
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_brightness(450)

sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
sensor.skip_frames(time = 500)
task_id = 0x00
index = 0
while True:
    img = sensor.snapshot()
    blobs = img.find_blobs(blue_thresholds,invert=True,merge=False)
    for blob in blobs:
        if abs(blob.h() - blob.w()) > 25 or blob.area() < 5300 or blob.area() > 14000 or blob.pixels()/(blob.w()*blob.h()) < 0.40:
            continue
        else:
            #result_dict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0}
            obj_img = img.copy(1,1,roi=blob.rect())
            #img.draw_rectangle(blob.rect())
            #for i in range(5):
            scores = tf.classify(net,obj_img,min_scale=1.0, scale_mul=0.5, x_overlap=0.0, y_overlap=0.0)[0].output()
            max_score = max(scores)
            max_label = scores.index(max_score)
            #result_dict[max_label] += 1
        #if max(result_dict,key=result_dict.get) != index:
        if max_label != index:
            img.draw_rectangle(blob.rect(),color = (255,0,0))
            print("error")
            obj_img = img.copy(1,1,roi=blob.rect())
            #obj_img.save('/sd/data/'+ str(labels[index]) + '//' + str(pyb.rng()) + '.bmp')
        else:
            img.draw_rectangle(blob.rect(),color = (0,255,0))
            print(max_label,labels[max_label])
        #obj_img.save('/sd/data8/'+ str(labels[index]) + '//' + str(pyb.rng()) + '.bmp')
