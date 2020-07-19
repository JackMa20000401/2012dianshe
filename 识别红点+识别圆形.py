import cv2
import numpy as np
import time
from collections import  deque
cap = cv2.VideoCapture(0)
#设定红色阈值，HSV空间
redLower = np.array([170, 100, 100])
redUpper = np.array([179, 255, 255])
#初始化追踪点的列表
mybuffer = 64
pts = deque(maxlen=mybuffer)
#打开摄像头
camera = cv2.VideoCapture(0)
#等待两秒
time.sleep(2)
#遍历每一帧，检测激光红点

while True:
    success, img = cap.read()
    if not success:
        print('No Camera')
        break
    # 转到HSV空间
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 根据阈值构建掩膜
    mask = cv2.inRange(hsv, redLower, redUpper)
    # 腐蚀操作
    mask = cv2.erode(mask, None, iterations=2)
    # 膨胀操作，其实先腐蚀再膨胀的效果是开运算，去除噪点
    mask = cv2.dilate(mask, None, iterations=2)
    # 轮廓检测
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    # 初始化光点轮廓轮廓质心
    center = None
    if len(cnts) > 0:
        #找到面积最大的轮廓
        c = max(cnts, key = cv2.contourArea)
        #确定面积最大的轮廓的外接圆
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        #计算轮廓的矩
        M = cv2.moments(c)
        #计算质心
        center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
        #只有当半径大于10时，才执行画图
        if radius > 10:
            cv2.circle(img, center, 5, (255, 0, 0), -1)
            #把质心添加到pts中，并且是添加到列表左侧
            pts.appendleft(center)

    imgMedian = cv2.medianBlur(img,3)
    gray = cv2.cvtColor(imgMedian, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 100, 240, 0)
    imgCanny = cv2.Canny(img, 20, 200)
    imgHough = cv2.HoughCircles(imgCanny, cv2.HOUGH_GRADIENT,1,100,param1=100, param2=150, minRadius=5,maxRadius=400)

    if type(imgHough) is np.ndarray:
        for circle in imgHough[0]:

            x = int(circle[0])
            y = int(circle[1])
            r = int(circle[2])
            print(x, y)
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1, 10)
            cv2.circle(img, (x, y), r, (0, 0, 255), 5)
    else:
        pass
    cv2.imshow("out", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()







