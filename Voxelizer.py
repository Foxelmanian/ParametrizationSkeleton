import os
import numpy as np
import vtk
from Module import Module
import trimesh

class Voxelizer(Module):
    def __init__(self, stl_path: str, number_of_voxels=200, model_is_valid=True, binvox_path='binvox.exe'):
        super().__init__()
        self.__stl_file_path = stl_path
        self.__number_of_voxels = number_of_voxels
        self.__binvox_path = binvox_path
        self.__use_3d_model = True
        self.__model_is_valid = model_is_valid

    def run(self, data=None):
        type = 'vtk'
        if self.__model_is_valid:
            mesh = trimesh.load_mesh(self.__stl_file_path)
            if not mesh.is_watertight:
                print('2D Object is found')
                self.__use_3d_model = False
        if self.__use_3d_model:
            self.__is_2D_3D_command = ''
        else:
            self.__is_2D_3D_command = '-e'

        bin_vtk_file = self.__stl_file_path[0:-4] + f'.{type}'
        if os.path.exists(bin_vtk_file):
            os.remove(bin_vtk_file)
        print("Voxel command: ", self.__get_binvox_call_command())
        os.system(self.__get_binvox_call_command(type=type))
        # Read voxel model save it and return it ad an array
        m1 = self.__import_vtk_array(bin_vtk_file)

        # Genearting voxel model in binvox format -->
        type = 'binvox'
        bin_vtk_file = self.__stl_file_path[0:-4] + f'.{type}'
        if os.path.exists(bin_vtk_file):
            os.remove(bin_vtk_file)
        print("Voxel command: ", self.__get_binvox_call_command())
        os.system(self.__get_binvox_call_command(type=type))
        return {'voxel_model': m1.data.tolist()}

    def __import_vtk_array(self, filename, vtk_data_type="point"):
        # Read the File data
        reader = vtk.vtkStructuredPointsReader()
        reader.SetFileName(filename)
        reader.ReadAllVectorsOn()
        reader.ReadAllScalarsOn()
        reader.Update()
        data = reader.GetOutput()
        # Different data types
        if vtk_data_type == "point":
            voxel_data = data.GetPointData().GetArray('voxel_data')
        else:
            voxel_data = data.GetCellData().GetArray('voxel_data')
        dim = data.GetDimensions()
        empty_voxel_model = np.zeros(data.GetNumberOfPoints()).astype(bool)
        for i in range(voxel_data.GetMaxId() + 1):
            if voxel_data.GetValue(i) != 0:
                empty_voxel_model[i] = True
        voxelized_model = empty_voxel_model.reshape(dim)
        voxelized_model = np.swapaxes(voxelized_model, 0, 2)
        return voxelized_model

    def __get_binvox_call_command(self, type='vtk') -> str:
        stl_file = self.__stl_file_path
        if not os.path.exists(stl_file):
            raise FileExistsError(stl_file)

        if type == 'vtk':
            command = self.__binvox_path + " " + \
                             stl_file + " -d " + \
                            str(self.__number_of_voxels) + " -t vtk " + self.__is_2D_3D_command
        else:
            command = self.__binvox_path + " " + \
                             stl_file + " -d " + \
                             str(self.__number_of_voxels) + " " + self.__is_2D_3D_command
                             #str(self.__number_of_voxels) + " -fit " + self.__is_2D_3D_command
        return command

