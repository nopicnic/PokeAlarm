import pickle
import os.path
import logging

log = logging.getLogger('Cache')


# Cache for reverse geocode lookup
class Cache(object):

    def __init__(self, name):
        self.adr_cache = {}
        self.gym_cache = {}
        self.__name = name
        self.__pkl_file_adr = 'cached_{}_adr.pkl'.format(self.__name)
        self.__pkl_file_gym = 'cached_{}_gym.pkl'.format(self.__name)

    def load(self):
        self.adr_cache = self.load_pickle(self.__pkl_file_adr)
        self.gym_cache = self.load_pickle(self.__pkl_file_gym)

    # load the cache
    @staticmethod
    def load_pickle(file_name):
        if os.path.isfile(file_name):
            try:
                pickle_file = open(file_name, 'r+')
            except:
                pickle_file = None
        else:
            pickle_file = None

        if pickle_file is None:
            return {}

        try:
            cache = pickle.load(pickle_file)
            log.info("Loaded cache with {} entries".format(len(cache)))
            pickle_file.close()
            return cache
        except:
            return {}

    @staticmethod
    def save_pickle(cache, file_name):
        log.info("Saving cache with {} entries".format(len(cache)))
        pickle_file = open(file_name, 'w+')
        pickle.dump(cache, pickle_file)

    def save(self):
        self.save_pickle(self.adr_cache,self.__pkl_file_adr)
        self.save_pickle(self.gym_cache,self.__pkl_file_gym)

    def in_gym_cache(self,key):
        return key in self.gym_cache

    def get_gym(self,key):
        return self.gym_cache[key]

    def put_gym(self, key, gym):
        self.gym_cache[key] = gym

    def in_adr_cache(self, key):
        return key in self.adr_cache

    def put_adr(self, key, val):
        self.adr_cache[key] = val

    def get_adr(self, key):
        return self.adr_cache[key]
