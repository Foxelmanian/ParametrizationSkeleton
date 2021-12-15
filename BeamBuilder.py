from typing import List
import numpy as np
from scipy import interpolate
from BeamCore import BeamCore
from Module import Module

from Chain import Chain
from CrossSection import CrossSection
from Spline import Spline
from Beam import Beam
from SkeletonASCIIPhraser import SkeletonASCIIPhraser

class BeamBuilder(Module, BeamCore):
    def __init__(self, cross_section_stl_path, origin_mesh_path='', skele_file_export_path='',
                 center_spline_along_cross_sections=True):
        self.__skele_file_export_path = skele_file_export_path
        Module.__init__(self)
        BeamCore.__init__(self, origin_mesh_path, cross_section_stl_path)
        self.__cross_section_stl_path = cross_section_stl_path
        self.__do_center_spline_along_cross_sections = center_spline_along_cross_sections
        self.__interp_degree = 3

    def __get_splines(self, chains):
        splines = []
        # Calculate the spline functions
        cut_t = []
        for chain in chains:
            chain = Chain(**chain)
            [tck, u], [dt1, dt2] = self.get_interpolation_function(chain, interp_degree=self.__interp_degree)

            if tck != None:
                splines.append(Spline(t=tck[0].tolist(),
                                      x=tck[1][0].tolist(),
                                      y=tck[1][1].tolist(),
                                      z=tck[1][2].tolist(),
                                      degree=int(tck[2]),
                                      start_connection_id=chain.start_connection_id,
                                      end_connection_id=chain.end_connection_id))
                cut_t.append((dt1,dt2))
        return splines, cut_t

    def run(self, chains: List[Chain], size):
        # First of all get the spline values
        splines, cut_t =  self.__get_splines(chains)
        splines = self.fit_mesh(size, splines)
        # Find the corresponding beams

        beams = self.__regulize_beams(splines, cut_t)
        json_dict = []
        beam_3D_dic = []
        for beam in beams:
            json_dict.append(beam._asdict())
        mesh_dict = {'x': self._triangle_mesh_cross.vertices[:, 0].tolist(),
                     'y': self._triangle_mesh_cross.vertices[:, 1].tolist(),
                     'z': self._triangle_mesh_cross.vertices[:, 2].tolist(),
                     'faces': self._triangle_mesh_cross.faces.tolist()}

        skele_ascii_parser = SkeletonASCIIPhraser(self.__skele_file_export_path)
        skele_ascii_parser.save(beams)
        #exit()
        return {'beam_skeleton': json_dict, 'beam_3D_mesh': beam_3D_dic, 'mesh': mesh_dict}

    def __center_spline_along_cross_sections(self, cross_sections, spline):
        xc = []
        yc = []
        zc = []
        for section in cross_sections:
            x, y, z = section.get_3D_center_points()
            xc.append(x)
            yc.append(y)
            zc.append(z)

        tck, u = interpolate.splprep([xc, yc, zc], k=3)
        return Spline(t=tck[0].tolist(),
               x=tck[1][0].tolist(),
               y=tck[1][1].tolist(),
               z=tck[1][2].tolist(),
               degree=int(tck[2]),
               start_connection_id=spline.start_connection_id,
               end_connection_id=spline.end_connection_id)

    def __regulize_beams(self, splines, cut_t):
        print('[i] Get Cross section profile along beam')
        beams = []
        for spline, cut_tt in zip(splines, cut_t):
            if self.__do_center_spline_along_cross_sections:
                try:
                    cross_sections = self.__get_cross_section_profil_along_beam(spline, interp_points=10)
                    # 1. Center to Cross Sections
                    spline = self.__center_spline_along_cross_sections(cross_sections, spline)
                except:pass
            cross_sections = self.__get_cross_section_profil_along_beam(spline, interp_points=0, u_fine=cut_tt)
            start_cross = cross_sections[0]
            end_cross = cross_sections[-1]

            if end_cross == None:
                end_xyz = None
                end_xy = None
            else:
                end_xyz = end_cross.get_xyz()
                end_xy = end_cross.get_xy()
            if start_cross == None:
                start_xyz = None
                start_xy = None
            else:
                start_xyz = start_cross.get_xyz()
                start_xy = start_cross.get_xy()

            beam = Beam(spline=spline,
                        crossSection1=[start_xyz,
                                       start_xy],
                        crossSection2=[end_xyz,
                                       end_xy],
                        cut_times=cut_tt)
            beams.append(beam)
        return beams

    def center_spline(self, profils_along_spline, spline):
        new_x = []
        new_y = []
        new_z = []
        for profil in profils_along_spline:
            center_point = profil.get_3D_center_points()
            new_x.append(center_point[0])
            new_y.append(center_point[1])
            new_z.append(center_point[2])

        tck, u = self.get_interpolation_function_xyz(new_x, new_y, new_z, spline.degree)
        return Spline(t=tck[0].tolist(),
                      x=tck[1][0].tolist(),
                      y=tck[1][1].tolist(),
                      z=tck[1][2].tolist(),
                      degree=int(tck[2]),
                      start_connection_id=spline.start_connection_id,
                      end_connection_id=spline.end_connection_id)

    def __get_spline_length(self, spline, interp_points=20):
        tck = [np.array(spline.t),
               [np.array(spline.x), np.array(spline.y), np.array(spline.z)],
               spline.degree]
        u_fine = np.linspace(0, 1, interp_points)
        r_square = 0
        [x_coordinates, y_coordinates, z_coordinates] = interpolate.splev(u_fine, tck)
        for x_coor1, y_coor1, z_coor1, x_coor2, y_coor2, z_coor2 in zip(x_coordinates[:-1], y_coordinates[:-1], z_coordinates[:-1],
                                                                        x_coordinates[1:], y_coordinates[1:], z_coordinates[1:]):
            r_square += (x_coor1 - x_coor2)**2 + (y_coor1 - y_coor2)**2 +(z_coor1 - z_coor2)**2
        return np.sqrt(r_square)


    def __get_cross_section_profil_along_beam(self, spline, interp_points=5, u_fine=None):
        # Build up the spline function and slices along this function

        tck = [np.array(spline.t),
               [np.array(spline.x), np.array(spline.y), np.array(spline.z)],
               spline.degree]
        if u_fine == None:
            u_fine = np.linspace(0, 1, interp_points)

        [x_coordinates, y_coordinates, z_coordinates] = interpolate.splev(u_fine, tck)
        [x_normals, y_normals, z_normals] = interpolate.splev(u_fine, tck, der=1)
        # Iterate to the number of interpolation points and build up the cross section distribution
        cross_sections = []
        for x, y, z, xn, yn, zn in zip(x_coordinates, y_coordinates, z_coordinates, x_normals, y_normals, z_normals):
            cross_section = self.find_cross_section((x, y, z),[xn, yn, zn],)
            if not cross_section == None:
                cross_sections.append(CrossSection(cross_section))
            else:
                cross_sections.append(None)
        return cross_sections

