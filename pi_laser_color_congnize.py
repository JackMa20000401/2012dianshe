import cv2
import numpy
import math

def wind_water(derta_x, derta_y): #八卦阵明辨方位, 彰道骨风后奇门
    tan = math.atan2(derta_y, derta_x)
    pi8 = math.pi / 8
    if derta_y < 0:
        if tan < -pi8 * 7 and tan > -math.pi:
            return 2
        elif tan < -pi8 * 5 and tan > -pi8 * 7:
            return 1
        elif tan < -pi8 * 3 and tan > -pi8 * 5:
            return 0
        elif tan < -pi8 and tan > -pi8 * 3:
            return 7
        elif tan < 0 and tan > -pi8:
            return 6
    if derta_y > 0:
        if tan > 0 and tan < pi8:
            return 6 #
        elif tan > pi8 and tan < pi8 * 3:
            return 5 #
        elif tan > pi8 * 3 and tan < pi8 * 5:
            return 4 #
        elif tan > pi8 * 5 and tan < pi8 * 7:
            return 3
        elif tan > pi8 * 7 and tan < math.pi:
            return 2

def thro_callback(x):
    global thro_data
    thro_data = x
    
def minDist_callback(x):
    global minDist
    minDist = x

def param1_callback(x):
    global param1
    param1 = x

def param2_callback(x):
    global param2
    param2 = x              #参数滑动条

def gloss_laser(red_x, red_y): # 激光点坐标的高斯滤波
    global laser_x, laser_y
    x = 0
    y = 0
    for a in range(4):
        laser_x[a] = laser_x[a + 1]
        laser_y[a] = laser_y[a + 1]
    laser_x[4] = red_x
    laser_y[4] = red_y
    for a in range(5):
        x += laser_x[a] * (a + 1)
        y += laser_y[a] * (a + 1)
    x = x // 15
    y = y // 15
    return x, y

def congnize_red(img): #找激光点的坐标
    global laser_x, laser_y, redLower, redUpper     #算法是将所有光斑的坐标取平均值
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  
    mask = cv2.inRange(hsv, redLower, redUpper)   #根据阈值构建掩膜
    mask = cv2.erode(mask, None, iterations=2)      #腐蚀操作
    mask = cv2.dilate(mask, None, iterations=2) #膨胀操作，其实先腐蚀再膨胀的效果是开运算，去除噪点
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    #初始化光点轮廓轮廓质心
    center = None  
    #如果存在轮廓  
    if len(cnts) > 0:  
        #找到面积最大的轮廓  
        c = max(cnts, key = cv2.contourArea)  
        #确定面积最大的轮廓的外接圆  
        ((x, y), radius) = cv2.minEnclosingCircle(c)  
        #计算轮廓的矩  
        M = cv2.moments(c)  
        #计算质心  
        center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))  
        return center[0], center[1]
    else:
        return laser_x[4], laser_y[4]

def gloss(new_x, new_y, new_length):        #靶区域圆的高斯滤波
    global buff_x, buff_y, buff_length
    x = 0
    y = 0
    lenth = 0
    for a in range(4):
        buff_x[a] = buff_x[a + 1]
        buff_y[a] = buff_y[a + 1]
        buff_length[a] = buff_length[a + 1] 
    buff_x[4] = new_x
    buff_y[4] = new_y
    buff_length[4] = new_length
    for a in range(5):
        x += buff_x[a] * (a + 1)
        y += buff_y[a] * (a + 1)
        lenth += buff_length[a] * (a + 1)
    x = x // 15
    y = y // 15
    lenth = lenth // 15
    return x, y, lenth

buff_length = [0, 0, 0, 0, 0]
buff_x = [0, 0, 0, 0, 0]
buff_y = [0, 0, 0, 0, 0] #高斯滤波缓存区创建
laser_x = [0, 0, 0, 0, 0]
laser_y = [0, 0, 0, 0, 0]
x = 0
y = 0
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cv2.namedWindow('source', cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('minDist', 'source', 25, 50, minDist_callback)
cv2.createTrackbar('param1', 'source', 50, 200, param1_callback)
cv2.createTrackbar('param2', 'source', 50, 200, param2_callback)
minDist = 25
param1 = 50
param2 =50
while cap.isOpened():
    ret, img = cap.read()
    if ret:
        max_cricle = [0, 0, 0]
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        canny_img = cv2.Canny(gray_img, 100, 200)   #边缘检测
        circles = cv2.HoughCircles(canny_img, cv2.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=0, maxRadius=0)
        #霍夫变换检测圆
        if type(circles) is numpy.ndarray:
            circles = numpy.uint16(numpy.around(circles))
            for i in circles[0, :]:
                if max_cricle[2] < i[2]:
                    max_cricle[0] = i[0]
                    max_cricle[1] = i[1]
                    max_cricle[2] = i[2]        #找到最大的圆以及它的圆心坐标
            x, y, length = gloss(max_cricle[0], max_cricle[1], max_cricle[2])
            cv2.circle(img, (x, y), length, (0, 255, 0), 2)
            cv2.circle(img, (x, y), 3, (0, 255, 0), 2)      #将圆标出
        cv2.imshow('source', img)
        cv2.imshow('gray', gray_img)
        cv2.imshow('canny', canny_img)
        key = cv2.waitKey(1)
        if key == ord('v'): #按下v停止读取摄像头图像, 开启鹰眼
            while True:
                key = cv2.waitKey(1)
                if key == ord(' '):
                    break
                if key == ord('v'):  #这样会使窗口停止刷新, 便于确定是否识别好了
                    break
            if key == ord(' '):     #对结果满意就按空格结束识别过程
                break
            if key == ord('v'):     #继续鹰眼
                continue
#开始识别激光点
d = length / 6
d_2 = d * 2
d_3 = d * 3
d_4 = d * 4
d_5 = d * 5
d_6 = d * 6
center = [y, x]
redLower = numpy.array([170, 100, 100])  #设定红色阈值，HSV空间  
redUpper = numpy.array([179, 255, 255])  
mybuffer = 64  #初始化追踪点的列表  
cv2.destroyWindow('gray')
cv2.destroyWindow('canny')  #删除不用的窗口
cv2.namedWindow('Black', cv2.WINDOW_AUTOSIZE)
cv2.createTrackbar('thro_data', 'Black', 250, 255, thro_callback)#调节二值化阈值的滑动条
while cap.isOpened():
    ret, img = cap.read()
    if ret:
        red_x, red_y = congnize_red(img)
        x, y = gloss_laser(red_x, red_y)            #快乐的高斯滤波
        derta_x = x - center[1]
        derta_y = y - center[0]
        distance = pow(pow(derta_x, 2) + pow(derta_y, 2), 0.5)
        if distance < d:
            print('正中', '一环')
            # cv2.putText(img, '8', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            # cv2.putText(img, '1', (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 202, 82), 2)
        else:
            direction = wind_water(derta_x, derta_y)
            if direction == 0:
                print('正上', end='')
                # cv2.putText(img, '0', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
                # cv2.putText(img, '1', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 202, 82), 2)
            elif direction == 1:
                print('左上', end='')
                # cv2.putText(img, '1', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            elif direction == 2:
                print('正左', end='')
                # cv2.putText(img, '2', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            elif direction == 3:
                print('左下', end='')
                # cv2.putText(img, '3', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            elif direction == 4:
                print('正下', end='')
                # cv2.putText(img, '4', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            elif direction == 5:
                print('右下', end='')
                # cv2.putText(img, '5', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            elif direction == 6:
                print('正右', end='')
                # cv2.putText(img, '6', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            elif direction == 7:
                print('右上', end='')
                # cv2.putText(img, '7', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (82, 173, 232), 2)
            if distance < d_2:
                print(' 二环')
                # cv2.putText(img, '2', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 202, 82), 2)
            elif distance < d_3:
                print(' 三环')
                # cv2.putText(img, '3', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 202, 82), 2)
            elif distance < d_4:
                print(' 四环')
                # cv2.putText(img, '4', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 202, 82), 2)
            elif distance < d_5:
                print(' 五环')
                # cv2.putText(img, '5', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 202, 82), 2)
            elif distance < d_6:
                print(' 六环')
                # cv2.putText(img, '6', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 202, 82), 2)
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1) #标记
        cv2.imshow('source picture', img)
        key = cv2.waitKey(1)
        if key == ord(' '):
            break
cap.release()
cv2.destroyAllWindows()