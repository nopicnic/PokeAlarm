import pickle
import os.path
import logging
import csv

log = logging.getLogger('Cache')

# Cache for reverse geocode lookup
class Cache(object):

    def __init__(self, name):
        self.adr_cache = {}
        self.gym_cache = {}
        self.__name = name
        self.__pkl_file_adr = 'cached_{}_adr.pkl'.format(name)
        self.__pkl_file_gym = 'cached_{}_gym.pkl'.format(name)

    def import_gym_csv(self, csv_filename):
        log.info("Importing {}".format(csv_filename))
        gyms = self.load_pickle(self.__pkl_file_gym)

        # Default column indexes in case we can't deduce from the header row
        gym_id_idx = 0
        gym_name_idx = 1
        gym_descr_idx = 2
        gym_url_idx = 3

        try:
            with open(csv_filename, 'rb') as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.read(), delimiters=';,')
                csv_file.seek(0)
                reader = csv.reader(csv_file,dialect)

                for row_idx, row in enumerate(reader):
                    if row_idx == 0:
                        # first row is header - lets find out what column is what
                        for column, header in enumerate(row):
                            if header == 'gym_id' or header == 'id':
                                gym_id_idx = column
                            elif header == 'name':
                                gym_name_idx = column
                            elif header == 'detail':
                                gym_descr_idx = column
                            elif header == 'url':
                                gym_url_idx = column
                    else:
                        log.info("parsing line {}".format(row))
                        gym = {
                            'id': row[gym_id_idx],
                            'name': row[gym_name_idx],
                            'description': row[gym_descr_idx],
                            'url': row[gym_url_idx]
                        }
                        gyms[row[gym_id_idx] ] = gym
        except:
            log.error("Something went wrong, your CSV is probably in the wrong format!")
            return

        if len(gyms) == 0:
            log.error("There was no gyms imported!!")
            return

        # Save imported gyms
        self.save_pickle(gyms,self.__pkl_file_gym)

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
