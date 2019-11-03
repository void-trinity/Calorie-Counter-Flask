import cv2 as cv
import numpy as np


density_dict = { 'apple': 0.7427, 'orange':0.94}
calorie_dict = { 'apple': 52, 'orange':89}

def detect_skin_alt(img):
    img = cv.imread(img)
    img = cv.resize(img, (1000, 1000))


    #Method 1
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)
    cv.imwrite('thumb1.jpg', thresh)

    kernel = np.ones((3, 3), np.uint8)
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=2)
    # sure background area
    sure_bg = cv.dilate(opening, kernel, iterations=3)
    # Finding sure foreground area
    dist_transform = cv.distanceTransform(opening, cv.DIST_L2, 5)
    ret, sure_fg = cv.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv.subtract(sure_bg, sure_fg)

    ret, markers = cv.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1
    # Now, mark the region of unknown with zero
    markers[unknown == 255] = 0

    markers = cv.watershed(img, markers)
    cv.imwrite('thumb2.jpg', markers)
    img[markers == -1] = [255, 0, 0]
    cv.imwrite('thumb3.jpg', img)











    #Method 2
    # lower = np.array([0, 48, 80], dtype="uint8")
    # upper = np.array([20, 255, 255], dtype="uint8")
    # converted = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # skinMask = cv.inRange(converted, lower, upper)
    # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (11, 11))
    # skinMask = cv.erode(skinMask, kernel, iterations=2)
    # skinMask = cv.dilate(skinMask, kernel, iterations=2)
    # skinMask = cv.GaussianBlur(skinMask, (3, 3), 0)
    # skin = cv.bitwise_and(img, img, mask=skinMask)
    # cv.imwrite('thumb.jpg', skin)

detect_skin_alt('Test/1 (76).jpg')

