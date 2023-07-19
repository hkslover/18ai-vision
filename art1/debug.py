import sensor
import math

# debug_item draw
# 1   a4_points_threshold
# 2   blue_threshold  3个art都要给
# debug_set (1，1)debug a4模式并且有绘制（包括a4纸、识别矩形和坐标位置都会标注，此时不能拍照取阈值）
# debug_set （1，0） 没有任何绘制 可以打开阈值编辑工具
debug_set = (1,1)
blue_thresholds = [(0, 100, -8, 79, -111, -10)]
points_threshold = (35, 72, -23, 127, -64, 127)
a4_threshold = (39, 100, -128, 127, -128, 127)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_brightness(450)
sensor.skip_frames(time = 100)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

while True:
	img = sensor.snapshot()
	if(debug_set[0] == 1):
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
                if(debug_set[1] == 1):
                	img.draw_rectangle(points_roi, color=(0, 255, 0))
                #for c in img.find_circles(roi =points_roi,threshold = 1400, x_margin = 1, y_margin = 1, r_margin = 1,r_min = 1, r_max =4, r_step = 1):
                    #img.draw_circle(c.x(), c.y(),2, color = (0, 0, 255),thickness = 2)
                #img.erode(1,thresold=7)
                points_list = []
                point_blobs = img.find_blobs([points_threshold], roi = points_roi,x_stride=1, y_stride=1,invert = True)
                for point_blob in point_blobs:
                    if point_blob.w() > 7 or point_blob.h() > 7:
                        continue
                    if(debug_set[1] == 1):
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
                print(points_list)
    elif(debug_set[0] == 2):
    	blobs = img.find_blobs(blue_thresholds,invert=True,merge=True,margin=2)
	    for blob in blobs:
	        if abs(blob.h() - blob.w()) > 25 or blob.area() < 5300 or blob.area() > 14000 or blob.pixels()/(blob.w()*blob.h()) < 0.50:
	            continue
	        if(debug_set[1] == 1):
	        	img.draw_rectangle(blob.rect(),color = (0,255,0))