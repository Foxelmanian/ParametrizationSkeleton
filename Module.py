from abc import ABCMeta
import os
import json



class Module(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def run(self, **args):
        # Return the Data
        print("[-] Run Method needs to be implemented")
        return None, 'not_implemented.txt'

    def _get_file_name(self):
        return self.__class__.__name__

    def save_data(self, storage_path, data):
        if data == None:
            raise ValueError(f'No Data to store {self.__name__}')
        if not os.path.exists(storage_path):
            os.mkdir(storage_path)
        with open(self.json_path(storage_path, self._get_file_name()), 'w') as outfile:
            json.dump(data, outfile)

    def delete_data(self, storage_path):

        if os.path.exists(self.json_path(storage_path, self._get_file_name())):
            os.remove(self.json_path(storage_path, self._get_file_name()))

    def json_path(self, storage_path, file_name):
        return os.path.join(storage_path, file_name + '.json')

    def load_data(self, storage_path):
        if not os.path.exists(self.json_path(storage_path, self._get_file_name())):
            return None
        with open(self.json_path(storage_path, self._get_file_name()), 'r') as infile:
            data = json.load(infile)
        return data

    def import_extern_data(self, json_path):
        if not os.path.exists(json_path):
            return None
        with open(json_path, 'r') as infile:
            data = json.load(infile)
        return data