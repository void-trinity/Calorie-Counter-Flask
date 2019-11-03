import cv2
import numpy as np
import os


def getAreaOfFood(img1):
    img1 = cv2.imread(img1)
    data = os.path.join(os.getcwd(), "images")
    if os.path.exists(data):
        print('folder exist for images at ', data)
    else:
        os.mkdir(data)
        print('folder created for images at ', data)

    img = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img_filt = cv2.medianBlur(img, 5)
    img_th = cv2.adaptiveThreshold(img_filt, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 2)
    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # make change here

    # find contours. sort. and find the biggest contour. the biggest contour corresponds to the plate and fruit.
    mask = np.zeros(img.shape, np.uint8)
    largest_areas = sorted(contours, key=cv2.contourArea)
    cv2.drawContours(mask, [largest_areas[-1]], 0, (255, 255, 255, 255), -1)
    img_bigcontour = cv2.bitwise_and(img1, img1, mask=mask)

    hsv_img = cv2.cvtColor(img_bigcontour, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_img)
    mask_plate = cv2.inRange(hsv_img, np.array([0, 0, 50]), np.array([200, 90, 250]))
    mask_not_plate = cv2.bitwise_not(mask_plate)
    fruit_skin = cv2.bitwise_and(img_bigcontour, img_bigcontour, mask=mask_not_plate)

    hsv_img = cv2.cvtColor(fruit_skin, cv2.COLOR_BGR2HSV)
    skin = cv2.inRange(hsv_img, np.array([0, 10, 60]), np.array([10, 160, 255]))  # Scalar(0, 10, 60), Scalar(20, 150, 255)
    not_skin = cv2.bitwise_not(skin);  # invert skin and black
    fruit = cv2.bitwise_and(fruit_skin, fruit_skin, mask=not_skin)  # get only fruit pixels

    fruit_bw = cv2.cvtColor(fruit, cv2.COLOR_BGR2GRAY)
    fruit_bin = cv2.inRange(fruit_bw, 10, 255)  # binary of fruit

    # erode before finding contours
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    erode_fruit = cv2.erode(fruit_bin, kernel, iterations=1)

    # find largest contour since that will be the fruit
    img_th = cv2.adaptiveThreshold(erode_fruit, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    mask_fruit = np.zeros(fruit_bin.shape, np.uint8)
    largest_areas = sorted(contours, key=cv2.contourArea)
    cv2.drawContours(mask_fruit, [largest_areas[-2]], 0, (255, 255, 255), -1)

    # dilate now
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_fruit2 = cv2.dilate(mask_fruit, kernel2, iterations=1)
    fruit_final = cv2.bitwise_and(img1, img1, mask=mask_fruit2)

    # find area of fruit
    img_th = cv2.adaptiveThreshold(mask_fruit2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    largest_areas = sorted(contours, key=cv2.contourArea)
    fruit_contour = largest_areas[-2]
    fruit_area = cv2.contourArea(fruit_contour)

    # finding the area of skin. find area of biggest contour
    skin2 = skin - mask_fruit2
    # erode before finding contours
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    skin_e = cv2.erode(skin2, kernel, iterations=1)
    img_th = cv2.adaptiveThreshold(skin_e, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    mask_skin = np.zeros(skin.shape, np.uint8)
    largest_areas = sorted(contours, key=cv2.contourArea)
    cv2.drawContours(mask_skin, [largest_areas[-2]], 0, (255, 255, 255), -1)

    skin_rect = cv2.minAreaRect(largest_areas[-2])
    box = cv2.boxPoints(skin_rect)
    box = np.int0(box)
    mask_skin2 = np.zeros(skin.shape, np.uint8)
    cv2.drawContours(mask_skin2, [box], 0, (255, 255, 255), -1)

    pix_height = max(skin_rect[1])
    pix_to_cm_multiplier = 5.0 / pix_height
    skin_area = cv2.contourArea(box)

    return fruit_area, fruit_bin, fruit_final, skin_area, fruit_contour, pix_to_cm_multiplier


# density - gram / cm^3
density_dict = {1: 0.609, 2: 0.94, 3: 0.641, 4: 0.641, 5: 0.513, 6: 0.482, 7: 0.481}
# kcal
calorie_dict = {1: 52, 2: 89, 3: 41, 4: 16, 5: 40, 6: 47, 7: 18}
# skin of photo to real multiplier
skin_multiplier = 5 * 2.3


def getCalorie(label, volume):  # volume in cm^3
    calorie = calorie_dict[int(label)]
    density = density_dict[int(label)]
    mass = volume * density * 1.0
    calorie_tot = (calorie / 100.0) * mass
    return mass, calorie_tot, calorie  # calorie per 100 grams


def getVolume(label, area, skin_area, pix_to_cm_multiplier, fruit_contour):
    area_fruit = (area / skin_area) * skin_multiplier  # area in cm^2
    label = int(label)
    volume = 100
    if label == 1 or label == 5 or label == 7 or label == 6:  # sphere-apple,tomato,orange,kiwi,onion
        radius = np.sqrt(area_fruit / np.pi)
        volume = (4 / 3) * np.pi * radius * radius * radius
    # print (area_fruit, radius, volume, skin_area)

    if label == 2 or label == 4 or (label == 3 and area_fruit > 30):  # cylinder like banana, cucumber, carrot
        fruit_rect = cv2.minAreaRect(fruit_contour)
        height = max(fruit_rect[1]) * pix_to_cm_multiplier
        radius = area_fruit / (2.0 * height)
        volume = np.pi * radius * radius * height

    if (label == 4 and area_fruit < 30):  # carrot
        volume = area_fruit * 0.5  # assuming width = 0.5 cm

    return volume


def calories(result, img):
    img_path = img  # "C:/Users/M Sc-2/Desktop/dataset/FooD/"+str(j)+"_"+str(i)+".jpg"
    fruit_areas, final_f, areaod, skin_areas, fruit_contours, pix_cm = getAreaOfFood(img_path)
    volume = getVolume(result, fruit_areas, skin_areas, pix_cm, fruit_contours)
    mass, cal, cal_100 = getCalorie(result, volume)
    fruit_volumes = volume
    fruit_calories = cal
    fruit_calories_100grams = cal_100
    fruit_mass = mass
    print("\nfruit_volumes",fruit_volumes,"\nfruit_calories",fruit_calories,"\nruit_calories_100grams",fruit_calories_100grams,"\nfruit_mass",fruit_mass)
    return fruit_calories


print(round(calories('2','Test/1 (6).jpg')))
