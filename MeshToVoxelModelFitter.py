import numpy as np
from typing import List
from Size import Size
from Spline import Spline

class MeshToVoxelFitter(object):

    def __init__(self, triangle_mesh):
        self.__triangle_mesh = triangle_mesh

    def fit_voxel_model_into_mesh(self, size, spline_representation):

        triangle_mesh = self.__triangle_mesh
        x_min = np.min(triangle_mesh.vertices[:, 0])
        x_max = np.max(triangle_mesh.vertices[:, 0])
        x_range = x_max - x_min
        y_min = np.min(triangle_mesh.vertices[:, 1])
        y_max = np.max(triangle_mesh.vertices[:, 1])
        y_range = y_max - y_min
        z_min = np.min(triangle_mesh.vertices[:, 2])
        z_max = np.max(triangle_mesh.vertices[:, 2])
        z_range = z_max - z_min

        size = Size(**size)
        new_splines = []

        for spline in spline_representation:
            # Elements to scale
            t = spline.t
            cx = spline.x
            cy = spline.y
            cz = spline.z
            # Scale the things
            # Scale the cross secteion
            cx = x_range / float(size.x_max - size.x_min) * cx
            cy = y_range / float(size.y_max - size.y_min) * cy
            cz = z_range / float(size.z_max - size.z_min) * cz

            # Move the cross section
            # push the model
            cx = cx + np.min(triangle_mesh.vertices[:, 0]) - size.x_min
            cy = cy + np.min(triangle_mesh.vertices[:, 1]) - size.y_min
            cz = cz + np.min(triangle_mesh.vertices[:, 2]) - size.z_min

            if spline.start_connection_id != None:
                c1x, c1y, c1z = spline.start_connection_id
                c1x = x_range / float(size.x_max - size.x_min) * c1x
                c1y = y_range / float(size.y_max - size.y_min) * c1y
                c1z = z_range / float(size.z_max - size.z_min) * c1z

                # Move the cross section
                # push the model
                c1x = c1x + np.min(triangle_mesh.vertices[:, 0]) - size.x_min
                c1y = c1y + np.min(triangle_mesh.vertices[:, 1]) - size.y_min
                c1z = c1z + np.min(triangle_mesh.vertices[:, 2]) - size.z_min
                c1_end = [float(c1x), float(c1y), float(c1z)]
            else:
                c1_end = None

            if spline.end_connection_id != None:
                c2x, c2y, c2z = spline.end_connection_id
                c2x = x_range / float(size.x_max - size.x_min) * c2x
                c2y = y_range / float(size.y_max - size.y_min) * c2y
                c2z = z_range / float(size.z_max - size.z_min) * c2z

                # Move the cross section
                # push the model
                c2x = c2x + np.min(triangle_mesh.vertices[:, 0]) - size.x_min
                c2y = c2y + np.min(triangle_mesh.vertices[:, 1]) - size.y_min
                c2z = c2z + np.min(triangle_mesh.vertices[:, 2]) - size.z_min
                c2_end = [float(c2x), float(c2y), float(c2z)]
            else:
                c2_end = None



            new_splines.append(Spline(t=t, x=cx.tolist(), y=cy.tolist(), z=cz.tolist(), degree=spline.degree,
                                      start_connection_id=c1_end, end_connection_id=c2_end))
        return new_splines

    def fit_mesh_into_voxel_model(self, voxel_model):
        # Now fitting the model into the cube mesh
        triangle_mesh = self.__triangle_mesh
        x_min = np.min(triangle_mesh.vertices[:, 0])
        x_max = np.max(triangle_mesh.vertices[:, 0])
        x_range = x_max - x_min
        y_min = np.min(triangle_mesh.vertices[:, 1])
        y_max = np.max(triangle_mesh.vertices[:, 1])
        y_range = y_max - y_min
        z_min = np.min(triangle_mesh.vertices[:, 2])
        z_max = np.max(triangle_mesh.vertices[:, 2])
        z_range = z_max - z_min
        xx, yy, zz = np.where(voxel_model==True)
        x_p_min = np.min(xx)
        x_p_max = np.max(xx)
        y_p_min = np.min(yy)
        y_p_max = np.max(yy)
        z_p_min = np.min(zz)
        z_p_max = np.max(zz)

        # SCALE triangle mesh modell
        triangle_mesh.vertices[:, 0] = float(x_p_max - x_p_min) / x_range * triangle_mesh.vertices[:, 0]
        triangle_mesh.vertices[:, 1] = float(y_p_max - y_p_min) / y_range * triangle_mesh.vertices[:, 1]
        triangle_mesh.vertices[:, 2] = float(z_p_max - z_p_min) / z_range * triangle_mesh.vertices[:, 2]

        # push the model
        triangle_mesh.vertices[:, 0] = triangle_mesh.vertices[:, 0] - np.min(triangle_mesh.vertices[:, 0]) + x_p_min
        triangle_mesh.vertices[:, 1] = triangle_mesh.vertices[:, 1] - np.min(triangle_mesh.vertices[:, 1]) + y_p_min
        triangle_mesh.vertices[:, 2] = triangle_mesh.vertices[:, 2] - np.min(triangle_mesh.vertices[:, 2]) + z_p_min
        return triangle_mesh