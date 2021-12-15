import os
import numpy as np
import scipy.ndimage as ndi
from Module import Module
from Size import Size
from MedialAxisThinning import MedialAxisThinning
from tvtk.tools import visual
from mayavi import mlab

class Skeletonizer(Module):

    def __init__(self,
                 method_is_lee94=True,
                 detect_only_robust_closed_skeleton_lines=False,
                 check_curve_end_point_sequentiell=False,
                 method_is_kal99=True,
                 skeletonizer_path='thinvox.exe',
                 binvox_model='',
                 data_storage_path='',
                 shared_voxel_number=2,
                 coarse_skeletonization = True, no_design_space_path=''):

        super().__init__()
        # Initialize Lee94 Skeleotnizer
        self.__method_is_lee94 = method_is_lee94
        self.__coarse_skeletonization = coarse_skeletonization
        if detect_only_robust_closed_skeleton_lines: method_is_kal99 = False
        if self.__coarse_skeletonization: method_is_kal99 = False

        self.__skel_Lee94 = MedialAxisThinning(preserve_only_homotopy=detect_only_robust_closed_skeleton_lines,
                                        check_curve_end_point_sequentiell=check_curve_end_point_sequentiell)
        self.__no_design_space = [], [], []
        self.__no_design_space_path = no_design_space_path

        data = self.import_extern_data(self.__no_design_space_path)
        if data != None:
            x_tmp, y_tmp, z_tmp, type_tmp= [], [], [], []
            for point in data['points']:
                x_tmp.append(point['x'])
                y_tmp.append(point['y'])
                z_tmp.append(point['z'])
                type_tmp.append(point['type'])
            self.__no_design_space = x_tmp, y_tmp, z_tmp
            self.__no_design_types = type_tmp
        self.__skel_Lee94.set_no_design_space(self.__no_design_space[0], self.__no_design_space[1], self.__no_design_space[2])


        thinvox_path = skeletonizer_path
        # Initialize kall 8 subiterations

        self.__shared_voxel_number=shared_voxel_number

        self.__no_design_types = []

    def get_voxel_surface_points(self, data):
        skel = np.pad(data, (1), 'constant')
        skel = skel.astype(int)
        x_size = len(skel)
        y_size = len(skel[0])
        z_size = len(skel[0][0])
        cands = np.zeros((x_size, y_size, z_size), dtype=int)
        for currentBorder in range(1, 7):
            if currentBorder == 1:
                y = np.array(list(range(1, y_size)))
                cands[:, y, :] += np.abs(skel[:, y, :] - skel[:, y - 1, :])

            elif currentBorder == 2:
                y = np.array(list(range(0, y_size - 1)))
                cands[:, y, :] += np.abs(skel[:, y, :] - skel[:, y + 1, :])

            elif currentBorder == 4:
                x = np.array(list(range(1, x_size)))
                cands[x, :, :] += np.abs(skel[x, :, :] - skel[x - 1, :, :])
            elif currentBorder == 3:
                x = np.array(list(range(0, x_size - 1)))
                cands[x, :, :] += np.abs(skel[x, :, :] - skel[x + 1, :, :])

            elif currentBorder == 6:
                z = np.array(list(range(1, z_size)))
                cands[:, :, z] += np.abs(skel[:, :, z] - skel[:, :, z - 1])
            elif currentBorder == 5:
                z = np.array(list(range(0, z_size - 1)))
                cands[:, :, z] += np.abs(skel[:, :, z] - skel[:, :, z + 1])

        cands = np.logical_and(skel, cands)
        cands = np.argwhere(cands != 0)
        x, y, z = cands[:, 0] - 1, cands[:, 1] - 1, cands[:, 2] - 1
        return (x,y,z)




    def run(self, voxel_model):
        voxel_model = np.array(voxel_model).astype(int)
        engine = mlab.get_engine()
        fig = mlab.figure(size=(600, 600), bgcolor=(1, 1, 1), fgcolor=(0.5, 0.5, 0.5))
        visual.set_viewer(fig)
        mlab.clf()

        point_selection = []
        voxel_model = np.array(voxel_model).astype(bool)
        x, y, z = np.where(voxel_model == True)
        x, y, z = self.get_voxel_surface_points(voxel_model)
        a = visual.Arrow(x=0, y=0, z=0, color=(0, 0, 0))
        a.actor.scale = [10, 10, 10]
        a.axis = [0, 0, 1]
        a1 = visual.Arrow(x=0, y=0, z=0, color=(0, 0, 0))
        a1.actor.scale = [10, 10, 10]
        a1.axis = [1, 0, 0]
        a2 = visual.Arrow(x=0, y=0, z=0, color=(0, 0, 0))
        a2.actor.scale = [10, 10, 10]
        a2.axis = [0, 1, 0]
        voxel_points = mlab.points3d(x, y, z, mode="cube", color=(115 /255, 115/255, 102/255), scale_factor=0.9 , opacity=1.0)
        if len(self.__no_design_space[0]) != 0:
            mlab.points3d(self.__no_design_space[0],
                          self.__no_design_space[1],
                          self.__no_design_space[2],
                          mode="sphere", color=(0 / 255, 255 / 255, 0 / 255), scale_factor=2.0,
                                         opacity=1.0)
        array_voxel = voxel_points.glyph.glyph_source.glyph_source.output.points.to_array()
        def picker_callback(picker_obj):
            picked = picker_obj.actors
            if voxel_points.actor.actor._vtk_obj in [o._vtk_obj for o in picked]:
                # m.mlab_source.points is the points array underlying the vtk
                # dataset. GetPointId return the index in this array.
                point_id = picker_obj.point_id / array_voxel.shape[0]
                if point_id != -1:
                    point_id = round(point_id)
                    mlab.points3d(x[point_id], y[point_id], z[point_id], mode="sphere", color=(255 / 255, 0 / 255, 0 / 255),
                              scale_factor=2.0, opacity=1.0)
                    point_selection.append((x[point_id], y[point_id], z[point_id]))

        picker = fig.on_mouse_pick(picker_callback)
        picker.tolerance = 0.001
        mlab.show()
        for (x, y, z) in point_selection:
            self.__no_design_space[0].append(x)
            self.__no_design_space[1].append(y)
            self.__no_design_space[2].append(z)
        skeletons = []
        # Active skeleton methods
        if self.__method_is_lee94:
            skeleton = self.__skel_Lee94.run(voxel_model)
            skeletons.append(skeleton)

        if len(skeletons) > 1:
            print(f'Combine skeletons {len(skeletons)}')
            combined_skeleton = skeletons[0].astype(int)
            for skeleton in skeletons[1:]:
                skeleton = skeleton.astype(int)
                combined_skeleton += skeleton
            # Use the existing skeleton information and combine them with the skeleton method according to lee
            no_x, no_y, no_z, types = [],[],[], []
            for x, y, z in np.argwhere(combined_skeleton >= self.__shared_voxel_number):
                no_x.append(int(x))
                no_y.append(int(y))
                no_z.append(int(z))
                types.append(5)
            self.__no_design_space[0].extend(no_x)
            self.__no_design_space[1].extend(no_y)
            self.__no_design_space[2].extend(no_z)
            self.__no_design_types.extend(types)

            # Connect al Skeleton with lee method
            skel_Lee94_con = MedialAxisThinning(preserve_only_homotopy=True,
                                                   check_curve_end_point_sequentiell=False)
            skel_Lee94_con.set_no_design_space(self.__no_design_space[0], self.__no_design_space[1], self.__no_design_space[2])
            skeleton = skel_Lee94_con.run(voxel_model)
            skeleton = skeleton.astype(bool)
        boundary_distance_map = ndi.distance_transform_edt(voxel_model)
        boundary_distance = boundary_distance_map[skeleton == True]
        skeleton = np.argwhere(skeleton == True)
        # Calculate size parameters
        xx, yy, zz = np.where(np.array(voxel_model).astype(bool))
        x_p_min, x_p_max = np.min(xx), np.max(xx)
        y_p_min, y_p_max = np.min(yy), np.max(yy)
        z_p_min, z_p_max = np.min(zz), np.max(zz)
        s = Size(int(x_p_min), int(x_p_max), int(y_p_min), int(y_p_max), int(z_p_min), int(z_p_max))
        no_design_space = []
        for xn, yn, zn, type in zip(self.__no_design_space[0], self.__no_design_space[1], self.__no_design_space[2], self.__no_design_types):
            no_design_space.append([xn,yn,zn, type])
        return {'skeleton': skeleton.tolist(),
                'boundary_distance': boundary_distance.tolist(),
                'size': s._asdict(),
                'no_design_space': no_design_space,
                'voxel_model': voxel_model.tolist()}



