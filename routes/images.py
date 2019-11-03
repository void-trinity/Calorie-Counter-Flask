from flask_restful import Resource, reqparse
import werkzeug
from flask import send_from_directory
from os import path, getcwd
import re
import json
import cv2 as cv
import numpy as np

import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()


density_dict = { 'apple': 0.7427, 'orange':0.94}
calorie_dict = { 'apple': 52, 'orange':89}


UPLOAD_FOLDER = 'static/img/'

def detect_skin(im):
    im_ycrcb = cv.cvtColor(im, cv.COLOR_BGR2YCR_CB)
    skin_ycrcb_mint = np.array((0, 133, 77))
    skin_ycrcb_maxt = np.array((255, 173, 127))
    skin_ycrcb = cv.inRange(im_ycrcb, skin_ycrcb_mint, skin_ycrcb_maxt)

    contours, hierarchy = cv.findContours(skin_ycrcb, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    largest_areas = sorted(contours, key=cv.contourArea)
    cv.drawContours(im, contours, -1, (255, 0, 0), 1)
    return cv.contourArea(largest_areas[-1]), im


def resize(x, factor):
    return round(x * factor / 100.0)


def get_area(img, object):
    name = img
    img = cv.imread('static/img/'+img)
    height, width = img.shape[:2]
    coords = object['rect']
    x = coords['x']
    y = coords['y']
    w = coords['w']
    h = coords['h']
    h = round(h * height)
    y = round(y * height)
    x = round(x * width)
    w = round(w * width)
    if height > 1000 or width > 1000:
        if height > width:
            scale_percent = height / 500
        else:
            scale_percent = width / 500
        width = resize(width, scale_percent)
        height = resize(height, scale_percent)
        dim = (width, height)
        x = resize(x, scale_percent)
        y = resize(y, scale_percent)
        w = resize(w, scale_percent)
        h = resize(h, scale_percent)
        img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
    rect = (x, y, w, h)
    orig_img = img
    mask = np.zeros(img.shape[:2], np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    cv.grabCut(img, mask, rect, bgd_model, fgd_model, 50, cv.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    img = img * mask2[:, :, np.newaxis]

    bw_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(bw_img, 0, 255, cv.THRESH_BINARY)

    count = cv.countNonZero(thresh)

    if count < 100:
        cv.imwrite(r'output/' + object['detectedClass'] + name, img)
        area, img = detect_skin(orig_img[y:y+h, x:x+w])
        return min(w * h, area)
    cv.imwrite(r'output/' + object['detectedClass'] + name, img)
    return count


def get_calorie(image, food):
    calories = 0
    thumb_area = get_area(image, food[-1])
    print('thumb_area: ', thumb_area)
    for i in range(len(food)-1):
        area = get_area(image, food[i])
        print('Food Area: ' + str(area))
        fruit_real_area = (area * 6 * 2.3) / thumb_area
        radius = np.sqrt(fruit_real_area / np.pi)
        volume = (4 / 3) * np.pi * radius * radius * radius
        print('volume: ' + str(volume))
        mass = volume * density_dict[food[i]['detectedClass']] * 1.0
        print('mass: ' + str(mass))
        calorie = (calorie_dict[food[i]['detectedClass']] / 100.0) * mass
        calories = calories + calorie
    return calories





class Upload_Image(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('image', type=werkzeug.datastructures.FileStorage, location='files')
            parser.add_argument('apple')
            parser.add_argument('orange')
            parser.add_argument('thumb')
            data = parser.parse_args()
            if data['image'] is None:
                return {'message': 'No file found', 'success': False}, 404
            photo1 = data['image']

            if photo1:
                filename = photo1.filename
                photo1.save(path.join(UPLOAD_FOLDER, filename))
                reg = r'^([\w]+-[\w]+)'
                filename = re.match(reg, filename).group()
            return {'message': 'Something went wrong', 'success': False}, 500
        except Exception as e:
            print(e)


class Get_Image(Resource):
    def get(self, image):
        if path.exists(getcwd() + '/' + UPLOAD_FOLDER + image):
            return send_from_directory(directory='static/img/', filename=image)
        return {'error': True}, 404


class Test_Upload(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('image', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('apple')
        parser.add_argument('orange')
        parser.add_argument('thumb')
        data = parser.parse_args()
        print(data)
        food = []
        if data['apple']:
            food.append(json.loads(data['apple']))
        if data['orange']:
            food.append(json.loads(data['orange']))
        if data['thumb']:
            food.append(json.loads(data['thumb']))
        photo1 = data['image']
        if photo1:
            filename = photo1.filename
            photo1.save(path.join(UPLOAD_FOLDER, filename))
            print(filename)
            reg = r'^([\w]+-[\w]+)'
            calories = get_calorie(filename, food)
            return {'success': True, 'calories': round(calories)}, 200

        return {'success': False}, 404
