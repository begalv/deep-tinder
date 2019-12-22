from photo import Photo

class Person():

    def __init__(self, data):
        self.__id = data['_id']
        self.__name = data['name']
        self.__distance = round(data['distance_mi'] / 0.62137, 2)
        self.__photos = self.__get_photos(data)
        self.__schools = self.__get_schools(data)


    def __repr__(self):
        return "{}, {}km away.".format(self.__name, self.__distance)


    def get_id(self):
        return self.__id


    def __get_photos(self, data):
        photos = []
        for photo in data['photos']:
            photos.append(Photo(photo['id'], photo['processedFiles'][2]['url']))
        return photos

    def __get_schools(self, data):
        schools = []
        try:
            for school in data['schools']:
                schools.append(school['name'])
            return schools
        except:
            return schools
