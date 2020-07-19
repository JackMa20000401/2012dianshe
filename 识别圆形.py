import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgMedian = cv2.medianBlur(img,3)
    gray = cv2.cvtColor(imgMedian, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 100, 240, 0)
    imgCanny = cv2.Canny(img, 20, 200)
    imgHough = cv2.HoughCircles(imgCanny, cv2.HOUGH_GRADIENT,1,100,param1=100, param2=100, minRadius=5,maxRadius=400)

    print(type(imgHough))
    if type(imgHough) is np.ndarray:
        for circle in imgHough[0]:
            print(circle[2])

            x = int(circle[0])
            y = int(circle[1])
            r = int(circle[2])
            cv2.circle(img, (x, y), 5, (0, 255, 0), -1, 10)
            cv2.circle(img, (x, y), r, (0, 0, 255), 5)
    else:
        pass

    cv2.imshow("gray", gray)
    cv2.imshow("canny", imgCanny)
    cv2.imshow("out", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
