import cv2
import numpy as np
cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    # Step1. 转换为HSV

    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    min_val, max_val, min_indx, max_indx = cv2.minMaxLoc(gray_image)
    print(min_val, max_val, min_indx, max_indx)
    cv2.circle(img,max_indx,10,(0, 255, 0),-1,3)
    cv2.putText(img, 'xiaochongjiu', max_indx,cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0,0),1,4)
    # for i in range(hue_image.shape[0]):
    #     for j in range(hue_image.shape[1]):
    #         if 180 >= hue_image[i, j, 0] >= 156 and 255 >= hue_image[i, j, 1] >= 43 and 255 >= hue_image[i, j, 2] >= 46:
    #             cv2.circle(img, (i, j), 1, (0, 0, 255), -1,5)




    # if circles is not None:
    #     x, y, radius = circles[0][0]
    #     center = (x, y)
    #     cv2.circle(img, center, radius, (0, 255, 0), 2)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cv2.imshow('result', img)
    cv2.imshow('Gray', gray_image)

cap.release()
cv2.destroyAllWindows()


