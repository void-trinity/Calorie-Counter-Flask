import numpy as np
import cv2

img = cv2.imread('static/img/trinity-1571667367846.jpg');
h = 0.23804175853729248
w = 0.32481488585472107
x = 0.0020821690559387207
y = 0.6653134226799011
height, width = img.shape[:2]

h = round(h*height)
y = round(y*height)
x = round(x*width)
w = round(w*width)
print(x, y, x+w, y+h)

cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 15)

cv2.imwrite("2afasf.jpg",img)

