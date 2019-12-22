import numpy as np
import requests
from PIL import Image, ImageDraw
from config import CONFIG
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
import cv2


class Photo():

    height = 216
    width = 172

    def __init__(self, id, url):
        self.__id = id
        self.__url = url
        self.__valid = False
        self.__pil_img =  self.__get_pil_img()
        self.__np_img = self.__to_np_array()
        self.__find_relevant_person()
        #self.__run_inference()


    def __repr__(self):
        return "url: " + self.__url


    def __get_pil_img(self):
        try:
            raw_img = requests.get(self.__url, stream=True).raw
            img = Image.open(raw_img)
            if img.size == (self.width, self.height):
                self.__valid = True
                img.save('./images/tmp/{}.jpeg'.format(self.__id), 'jpeg')
                return img
            else:
                return None
        except Exception as e:
            msg = "Something went wrong. Could not access image url."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data

    def __to_np_array(self, image=None):
        '''
        input: Photo's pillow image
        '''
        if self.__valid:
            if image != None:
                img = image
            else:
                img = self.__pil_img
            np_img = np.array(img.getdata())
            np_img = np_img.reshape((self.height, self.width, 3)).astype(np.uint8)
            return np_img
        else:
            return None


    def __run_inference(self):
        '''
        input: Photo's numpy array
        output: Inference information of object detection and panoptic segmentation
        obs: Runs inference on the photo using detectron2 api and coco dataset pre-trained models
        '''
        model_config = get_cfg()

        model_config.merge_from_file(CONFIG['paths']['coco_detection_cfg'])
        obj_predictor = DefaultPredictor(model_config)
        obj_output = obj_predictor(self.__np_img)

        model_config.merge_from_file(CONFIG['paths']['coco_panoptic_cfg'])
        panoptic_predictor = DefaultPredictor(model_config)
        panoptic_output = panoptic_predictor(self.__np_img)

        return obj_output['instances'], panoptic_output['panoptic_seg']


    def __find_relevant_person(self):
        '''
        input: Inference on the photo made by the object detection API
        output: Dict {"img": cropped image of the person on the photo, "coordinates": coordinates of that person on the real photo}
        obs: It discards photos with more than one person or no person at all, as well photos which the person represents less than 40% of the total image.
        '''
        if self.__valid:
            person_region = {'img':None, 'coordinates':None}
            obj_inference, panoptic_inference = self.__run_inference()
            if len(obj_inference.pred_boxes) > 0:
                for i in range(len(obj_inference.pred_boxes)):
                    person_count = 0
                    if obj_inference.pred_classes[i] == 0 and obj_inference.scores[i] >= 0.85:
                        person_count += 1
                        if person_count >= 2:
                            self.__valid = False
                            break
                        else:
                            person_coordinate = np.array(obj_inference.pred_boxes.tensor[i])
                            person_img = self.__pil_img.crop(person_coordinate)
                            if person_img.size > (self.width * 0.4, self.height * 0.4):
                                person_region['coordinates'] = person_coordinate
                                person_region['img'] = person_img
                            else:
                                self.__valid = False
                                break
                if self.__valid:
                    relevant_region = person_region['img']
                    relevant_region.save('./images/tmp/{}crop.jpeg'.format(self.__id), 'jpeg')
                    return person_region
                else:
                    return None
            else:
                self.__valid = False
                return None
        else:
            return None


    def download(self, dataset=False, folder="."):
        pass
