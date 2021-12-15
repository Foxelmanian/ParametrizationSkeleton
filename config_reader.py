import configparser
from RegisteredModules import RegisteredModules

class ConfigReader(object):

    def __init__(self, config_file_name):
        self.__configRead = configparser.ConfigParser()
        self.__configRead.read(config_file_name)

    def get_register_modules(self):
        section = self.__configRead['Module']
        active_modules = [module.name for key, module in zip(section, RegisteredModules)
                          if section.getboolean(key)]
        return active_modules

    def get_parameters(self, section_name):
        section = self.__configRead[section_name]
        parameters = {}
        for key in section: parameters[key] = self.__convert_string_to_argument(section[key])
        return parameters

    def __convert_string_to_argument(self, value):
        if value.isdigit():
            return int(value)
        if value.replace('.','',1).isdigit():
            return float(value)
        if value.lower() =='true':
            return True
        if value.lower() =='false':
            return False
        return value





