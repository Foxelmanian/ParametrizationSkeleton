
import os
import logging
from RegisteredModules import RegisteredModules
from config_reader import ConfigReader
import shutil
from typing import Dict

logging.basicConfig(filename='LogSkeletonBuilderController.log', level=logging.DEBUG)
logging.warning('An example message.')
logging.warning('Another message')

class SkeletonBuilderController(object):
    def __init__(self):
        self.FILE_NAME_MODEL = 'model'

        self.config_file_name = 'config.ini'
        if os.path.exists(self.config_file_name):
            print("Use Settings from config file")
            logging.info('Use Settings from config file')
            self.__config_reader = ConfigReader(self.config_file_name)
        else:
            print(f'No config file was found create one with: {self.config_file_name}')
            logging.error(f'No config file was found create one with: {self.config_file_name}')
            exit()


    def run(self):
        self.__start_active_modules(self.__config_reader.get_register_modules())

    def __start_active_modules(self, modules: Dict ):
        general_module_parameters = self.__config_reader.get_parameters('GENERAL')

        data_base_path = general_module_parameters['data_base_storage_path']

        for module_name in modules:
            # Import parameters and build up module
            print(f'Start Module: {module_name}')
            parms = self.__config_reader.get_parameters(section_name=module_name)

            if module_name == 'VOXELIZER':
                if not os.path.exists(data_base_path):
                    os.makedirs(data_base_path)
                if not os.path.exists(os.path.join(data_base_path, self.FILE_NAME_MODEL + '.stl')):
                    shutil.copy2(parms['stl_path'], os.path.join(data_base_path, self.FILE_NAME_MODEL + '.stl'))
                parms['stl_path'] = os.path.join(data_base_path, self.FILE_NAME_MODEL + '.stl')

            if module_name == 'SKELETONIZER':
                parms['data_storage_path'] = data_base_path
                parms['binvox_model'] = os.path.join(data_base_path, self.FILE_NAME_MODEL + '.binvox')
                #parms['binvox_model'] = os.path.join(data_base_path, self.FILE_NAME_MODEL + '.vtk')
            if module_name == 'BEAM_ANALYZER':
                parms['data_storage_path'] = data_base_path

            # Get the registered Module
            registered_module = RegisteredModules[module_name]
            module = registered_module.value(**parms)

            # Run or import data from the current module
            if module.load_data(general_module_parameters['data_base_storage_path']) == None or True:
                # Load data from previous module
                if module_name != 'VOXELIZER':
                    prev_registered_module = registered_module.get_previous_module()
                    print(f'{module_name}: Load Data from previous module {prev_registered_module.name}')
                    prev_parameters = self.__config_reader.get_parameters(section_name=prev_registered_module.name)
                    prev_module = prev_registered_module.value(**prev_parameters)

                    data = prev_module.load_data(general_module_parameters['data_base_storage_path'])
                    if module_name == 'CHAIN_BUILDER':
                        vox_module = registered_module.get_module('VOXELIZER')
                        vox_parameter = self.__config_reader.get_parameters(section_name=vox_module.name)
                        vox_module = vox_module.value(**vox_parameter)
                        vox_data = vox_module.load_data(general_module_parameters['data_base_storage_path'])

                        for key, value in zip(vox_data.keys(), vox_data.values()):
                            data[key] = value
                else:
                    print(f'{module_name}: Crate the data baseCopy the stl file into the data base')
                    if not os.path.exists(data_base_path):
                        os.mkdir(data_base_path)
                    print(f'{module_name}:Crate the data baseCopy the stl file into the data base')
                    if not os.path.exists(os.path.join(data_base_path, self.FILE_NAME_MODEL + '.stl')):
                        shutil.copy2(parms['stl_path'], os.path.join(data_base_path, self.FILE_NAME_MODEL + '.stl'))
                    data = {'data': None} # Voxelizer wont need any data --> so None
                print(f'{module_name}: Create new Data')
                module.delete_data(general_module_parameters['data_base_storage_path'])
                data = module.run(**data)
                module.save_data(general_module_parameters['data_base_storage_path'], data)
            else:
                print(f'{module_name}: Load Data from database: ')
                data = module.load_data(general_module_parameters['data_base_storage_path'])


