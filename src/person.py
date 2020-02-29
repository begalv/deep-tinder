from photo import Photo

class Person():

    def __init__(self, data, download_photos=False):
        self.__id = data['_id']
        self.__name = data['name']
        self.__distance = round(data['distance_mi'] / 0.62137, 2)
        self.__photos_data = data['photos']
        self.__photos = []
        self.__schools = self.__set_schools(data)
        if download_photos == True:
            self.__set__all_photos()
        else:
            self.__set_first_photo()


    def __repr__(self):
        return "{}, {}km away.".format(self.__name, self.__distance)


    def get_id(self):
        return self.__id

    def get_photos(self):
        return self.__photos

    def get_first_photo(self):
        if len(self.__photos) > 0:
            return self.__photos[0]
        else:
            return None

    def __set_first_photo(self):
        photo = self.__photos_data[0]
        if len(self.__photos) == 0:
            self.__photos.append(Photo(self.__id, photo['id'], photo['processedFiles'][1]['url']))
            return True
        else:
            return False


    def set_other_photos(self):
        if len(self.__photos) == 1:
            for photo in self.__photos_data[1:]:
                self.__photos.append(Photo(self.__id, photo['id'], photo['processedFiles'][1]['url']))
            return True
        else:
            return False


    def __set__all_photos(self):
        self.__set_first_photo()
        self.set_other_photos()


    def __set_schools(self, data):
        schools = []
        try:
            for school in data['schools']:
                schools.append(school['name'])
            return schools
        except:
            return schools
