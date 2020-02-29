import numpy as np
import requests
import yaml
import os
from PIL import Image
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

config_file = './settings/configs.yaml'
with open(config_file, 'r') as cfile:
    configs = yaml.full_load(cfile)

class Photo():

    height = 400
    width = 320

    def __init__(self, owner_id, id, url):
        self.__owner_id = owner_id
        self.__id = id                                      #string: photo's indivudual id
        self.__filename = "{}-{}.{}".format(self.__owner_id, self.__id, 'jpeg')
        self.__is_downloaded = self.__is_in_folder()
        self.__url = url                                    #string: photo's url on tinder servers
        self.__valid = False                                #bool: if the photo matches the neural net and dataset critereas
        self.__img =  self.__set_img()                      #Image object: photo's pillow image object
        self.__np_arr = self.__to_np_array()                #numpy array: photo's numpy array of raw data
        self.__person_img = self.__find_relevant_person()


    def __repr__(self):
        return self.__person_img


    def __is_in_folder(self):
        pos_folder = configs['paths']['pos']
        neg_folder = configs['paths']['neg']
        if os.path.isfile(os.path.join(pos_folder, self.__filename)) == False and os.path.isfile(os.path.join(neg_folder, self.__filename)) == False:
            return False
        else:
            return True


    def __set_img(self):
        '''
        input: Photo's url
        output: Photo's pillow image object | None | Request error data
        obs: It makes a request to tinder servers and opens the photo's raw data with pillow
        '''
        try:
            raw_img = requests.get(self.__url, stream=True).raw
            img = Image.open(raw_img).convert('RGB')
            if img.size == (self.width, self.height):
                self.__valid = True
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
        input: Photo's pillow image object | other pillow images passed through parameter
        output: Photo's 3d numpy array of uint8 elements | None
        '''
        if self.__valid:
            if image != None:
                img = image
                (w,h) = img.size
                size = (h, w, 3)
            else:
                img = self.__img
                size = (self.height, self.width, 3)
            np_arr = np.array(img.getdata())
            np_arr = np_arr.reshape(size).astype(np.uint8)
            return np_arr
        else:
            return None



    def __run_inference(self, np_arr=None):
        '''
        input: Photo's numpy array
        output: Inference information of object detection and rcnn masks | None
        obs: Runs inference on the photo using detectron2 api and coco dataset pre-trained models
        '''
        if self.__valid:
            try:
                if np_arr == None:
                    np_arr = self.__np_arr
                model_config = get_cfg()
                model_config.merge_from_file(configs['paths']['coco_segmentation_cfg'][0])
                predictor = DefaultPredictor(model_config)
                output = predictor(np_arr)
                return output['instances']
            except Exception as e:
                msg = "Something went wrong. Could not run inference on person's photo."
                print("{}\nError: {}".format(msg, e))
                error_data = {
                    "message": msg,
                    "error": e
                }
                return error_data
        else:
            return None



    def __find_relevant_person(self):
        '''
        input: Inference on the photo made by the object detection API
        output: Photo's version without the background, only the person | None
        obs: It discards photos with more than one person or no person at all, as well photos which the person represents less than 10% of the total image.
        '''
        if self.__valid:
            person_img = None
            sem_inference = self.__run_inference()
            if len(sem_inference.pred_boxes) > 0:
                person_count = 0
                for i in range(len(sem_inference.pred_boxes)):
                    if sem_inference.pred_classes[i] == 0 and sem_inference.scores[i] >= 0.9:
                        person_coordinate = np.array(sem_inference.pred_boxes.tensor[i])
                        person_crop_img = self.__img.crop(person_coordinate).convert('RGB')
                        if person_crop_img.size >= (self.width * 0.1, self.height * 0.1):
                            person_count += 1
                            if person_count >= 2:
                                self.__valid = False
                                person_img = None
                                break
                            else:
                                np_mask_arr = np.array(sem_inference.pred_masks[i]).astype(np.uint8)
                                mask = Image.fromarray((np_mask_arr * 255), mode = 'L').convert('1')
                                black_rgb_img = Image.new('RGB', (self.width, self.height), (0,0,0))
                                person_img = Image.composite(self.__img, black_rgb_img, mask)

                if person_img == None:
                    self.__valid = False
                return person_img
            else:
                self.__valid = False
                return None
        else:
            return None


    def download(self, label='tmp', format='jpeg'):
        '''
        input: path to download's folder, format of the download file
        output: True if image was downloaded
        obs: Downloads person's cutted photo to a folder
        '''
        if self.__valid and self.__is_downloaded == False:
            pos_folder = configs['paths']['pos']
            neg_folder = configs['paths']['neg']
            tmp_folder = configs['paths']['tmp']
            self.__person_img.save("{}{}".format(pos_folder if label=='pos' else neg_folder if label=='neg' else tmp_folder, self.__filename), format)
            return True
        else:
            return False
