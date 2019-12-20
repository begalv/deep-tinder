import tensorflow.compat.v1 as tf
import numpy as np
import requests
from PIL import Image
from config import CONFIG
import json
from object_detection.utils import ops as utils_ops


class Photo():

    def __init__(self, id, url):
        self.__id = id
        self.__url = url
        self.__pil_img =  self.__get_pil_img()
        self.__np_image = self.__to_np_array()
        self.find_person()


    def __repr__(self):
        return "url: " + self.__url


    def __get_pil_img(self):
        raw_img = requests.get(self.__url, stream=True).raw
        img = Image.open(raw_img)
        img.save('./images/tmp/{}.jpeg'.format(self.__id), 'jpeg')
        return img


    def __to_np_array(self):
        #pillow img object to a 3-d numpy array (rgb)
        (im_width, im_height) = self.__pil_img.size
        np_img = np.array(self.__pil_img.getdata())
        np_img = np_img.reshape((im_height, im_width, 3)).astype(np.uint8)
        return np_img


    def __run_inference_for_person_detection(self):
        img_np_exp = np.expand_dims(self.__np_image, axis=0)
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            #loading graph
            graph_def = tf.GraphDef()
            with tf.gfile.GFile(CONFIG['paths']['obj_detection_graph'], 'rb') as graph_file:
                graph_string = graph_file.read()
                graph_def.ParseFromString(graph_string)
                tf.import_graph_def(graph_def, name='')

            with tf.Session() as sess:
                #running inference
                operations = tf.get_default_graph().get_operations()
                tensors_names = []
                for operation in operations:
                    for output in operation.outputs:
                        tensors_names.append(output.name)

                tensors_dict = {}
                keys = ['num_detections', 'detection_boxes', 'detection_scores', 'detection_classes', 'detection_masks']
                for key in keys:
                    tensor_name = key + ':0'
                    if tensor_name in tensors_names:
                        tensors_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)

                if 'detection_masks' in tensors_dict:
                    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(detection_masks, detection_boxes, img_np_exp.shape[1], img_np_exp.shape[2])
                    detection_masks_reframed = tf.cast(tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    tensors_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)

                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
                output_dict = sess.run(tensors_dict, feed_dict={image_tensor: img_np_exp})


                output_dict['num_detections'] = int(output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.int64)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]

                print(output_dict)

                return output_dict


    def find_person(self):
        output_dict = self.__run_inference_for_person_detection()
        persons_coordinates = []
        for i in range(len(output_dict['detection_boxes'])):
            score = output_dict['detection_scores'][i]
            type = output_dict['detection_classes'][i]
            if score > 0.5 and type == 1:
                persons_coordinates.append(output_dict['detection_boxes'][i])

        w, h = self.__pil_img.size
        for person_coordinate in persons_coordinates:
            cropped_img = self.__pil_img.crop((
                int(w * person_coordinate[1]),
                int(h * person_coordinate[0]),
                int(w * person_coordinate[3]),
                int(h * person_coordinate[2]),
            ))
            cropped_img.save('./images/tmp/{}cropped.jpeg'.format(self.__id), 'jpeg')



    def download(self, dataset=False, folder="."):
        pass
