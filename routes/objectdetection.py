import cv2
import numpy as np
from flask_restful import Resource, reqparse
from os import getcwd, path

YOLO_PATH = getcwd() + '/yolo_assets/'
IMAGE_FOLDER = getcwd() + '/static/img/'


class ObjectModel(Resource):
    @classmethod
    def get(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('image', type=str, help='This field cannot be blank', required=True)

        data = parser.parse_args()
        image = data['image']

        if path.exists(IMAGE_FOLDER + image) is False:
            return {'success': False, 'message': 'File not found'}, 404

        object_list = cls.detect_objects(image)

        if object_list is not None:
            return {'objects': object_list, 'success': True}, 200
        return {'error': 'No objects found'}, 404

    @classmethod
    def detect_objects(cls, image):
        image_name = image
        image = cv2.imread(IMAGE_FOLDER + image)
        width = image.shape[1]
        height = image.shape[0]
        scale = 0.00392

        with open(YOLO_PATH + 'yolov3.txt', 'r') as f:
            classes = [line.strip() for line in f.readlines()]

        net = cv2.dnn.readNet(YOLO_PATH + 'yolov3.weights', YOLO_PATH + 'yolov3.cfg')
        blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(cls.get_output_layers(net))
        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        object_list = []

        for i in indices:
            box = boxes[i[0]]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            object_list.append({'name': classes[class_ids[i[0]]], 'x': box[0], 'y': box[1], 'w': box[2], 'h': box[3]})
            label = str(classes[class_ids[i[0]]])
            color = COLORS[class_ids[i[0]]]
            x=round(x)
            y=round(y)
            w=round(w)
            h=round(h)
            cv2.rectangle(image, (x, y), (x+w, y+h), color, round(height/100))
            cv2.putText(image, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, width/1000, color, round(height/200))

        cv2.imwrite(IMAGE_FOLDER + 'processed/' + image_name, image)
        return object_list

    @classmethod
    def get_output_layers(cls, net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers
