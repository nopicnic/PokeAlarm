import pickle


class Cache(object):

    # load the geocode cache
    def setup_geocache(self):
        geo_pickle_file = open('geocache.pkl', 'r+b')

        if geo_pickle_file is None:
            self.__geocache = {}
            return

        self.__geoccache = pickle.load(geo_pickle_file)

        geo_pickle_file.close()

    def save_geocache(self):
        geo_pickle_file = open('geocache.pkl', 'w+b')
        pickle.save(self.__geocache, geo_pickle_file)