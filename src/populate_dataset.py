import json
import yaml
import os
import tqdm
from tinder_api import Tinder_API

config_file = './settings/configs.yaml'
with open(config_file, 'r') as cfile:
    configs = yaml.full_load(cfile)

class data_populator():

    def __init__(self, tinder_api):
        self.__tinder_api = api
        self.__pos_count = 0
        self.__neg_count = 0
        self.__count = 0


    def __download_photos(self, person, label):
        try:
            photos = person.get_photos()
            count = 0
            if len(photos) > 0:
                for photo in photos:
                    if photo != None:
                        downloaded = photo.download(label=label)
                        if downloaded:
                            count += 1
            return count
        except:
            return 0


    def __update_info_file(self):
        info_file = './settings/infos.yaml'
        with open(info_file, 'r') as ifile:
            infos = yaml.full_load(ifile)
        infos['dataset']['pos_count'] += self.__pos_count
        infos['dataset']['neg_count'] += self.__neg_count
        infos['dataset']['total_count'] += self.__count
        os.remove(info_file)
        with open(info_file, 'w') as ifile:
            yaml.dump(infos, ifile)
        self.__pos_count = 0
        self.__neg_count = 0
        self.__count = 0


    def populate_from_json(self, like_ratio=25):
        json_file = 'previously_swiped.json'
        try:
            with open(json_file, 'r') as sfile:
                swipes = json.load(sfile)
                bar = tqdm.tqdm(total=len(swipes['previouslySwiped']), desc='Populating from json')
                for i, swipe in enumerate(swipes['previouslySwiped']):
                    if swipe['rating'] == 'like' or swipe['rating'] == 'superlike':
                        person = self.__tinder_api.get_person(swipe['id'], download_photos=True)
                        downloaded_count = self.__download_photos(person, 'pos')
                        self.__pos_count += downloaded_count
                        self.__count += downloaded_count
                    else:
                        if i % like_ratio == 0:
                            person = self.__tinder_api.get_person(swipe['id'], download_photos=True)
                            downloaded_count = self.__download_photos(person, 'neg')
                            self.__neg_count += downloaded_count
                            self.__count += downloaded_count
                    bar.update(1)
            self.__update_info_file()
            os.remove(json_file)
            open(json_file, 'a').close()
        except Exception as e:
            msg = "Something went wrong. Could not populate from json."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data


    def populate_from_matches(self, last_matches=10):
        try:
            matches = self.__tinder_api.get_matches(last_matches)
            for match in matches:
                downloaded_count = self.__download_photos(match, 'pos')
                self.__pos_count += downloaded_count
                self.__count += downloaded_count
            self.__update_info_file()
        except Exception as e:
            msg = "Something went wrong. Could not populate from matches."
            print("{}\nError: {}".format(msg, e))
            error_data = {
                "message": msg,
                "error": e
            }
            return error_data


if __name__ == '__main__':

    username = configs['fb_login']['username']
    password = configs['fb_login']['password']
    api = Tinder_API(username, password)
    populator = data_populator(api)

    while True:
        ipt = input("Populate from json or from matches? (j/m): ").lower().strip()
        if ipt in ['j', 'json', 'm', 'matches', 'match']:
            break
        else:
            print("Invalid choice. please try again.")

    if ipt in ['j', 'json']:
        populator.populate_from_json(like_ratio=33)
    else:
        populator.populate_from_matches(last_matches=14)
