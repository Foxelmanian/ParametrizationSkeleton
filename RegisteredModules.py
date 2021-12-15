from enum import Enum, auto
from Skeletonizer import Skeletonizer
from Voxelizer import Voxelizer
from Classifier import Classifier
from ChainBuilder import ChainBuilder
from BeamBuilder import BeamBuilder


order = 'VOXELIZER SKELETONIZER CLASSIFIER CHAIN_BUILDER BEAM_BUILDER'
class RegisteredModules(Enum):
    _order_ = order
    VOXELIZER = Voxelizer
    SKELETONIZER = Skeletonizer
    CLASSIFIER = Classifier
    CHAIN_BUILDER = ChainBuilder
    BEAM_BUILDER = BeamBuilder


    def get_previous_module(self):
        module_names = order.split(' ')
        if self.name == module_names[0]:
            raise NotImplementedError('No previous module exists')
        prev_module_index = module_names.index(self.name) - 1
        return RegisteredModules[module_names[prev_module_index]]

    def get_module(self, name):
        module_names = order.split(' ')
        for modue_name in module_names:
            if modue_name == name:
                module_index = module_names.index(name)
                return RegisteredModules[module_names[module_index]]
        raise NotImplementedError(f'Module not found {name}')
