import numpy as np
from scipy import interpolate
class SkeletonASCIIPhraser(object):

    def __init__(self, export_path):

        self.__export_path = export_path

    def save(self, beams):
        file = open(self.__export_path, 'w')
        self.__plot_analytical_skeleton_beams(file, beams)
        file.close()

    def __plot_analytical_skeleton_beams(self, file, beams):
        # Save the ids and the export to the ids in a dictionary
        point_ids = {}
        vector_ids = {}
        spline_ids = {}
        curve_ids = {}
        cross_sections_ids = {}
        beam_ids = {}
        junction_connections = {}
        # ID counters
        point_id = 0
        spline_id = 0
        curve_id = 0
        vector_id = 0
        cross_section_id = 0
        beam_id = 0
        junction_id_point_list = {}
        start_end_cross_section_correspondence = {}

        for beam in beams:
            spline = beam.spline
            # calculate points
            point_id += 1
            p_jun_start_id = point_id
            point_ids[point_id] = [spline.x[0], spline.y[0], spline.z[0]]
            point_id += 1
            # Save point to point id
            point_ids[point_id] = [spline.x[-1], spline.y[-1], spline.z[-1]]
            p_jun_end_id = point_id
            # Calculate vectors
            vector_id += 1
            # Build up vector + id
            n_x1 = spline.degree * (spline.x[0] - spline.x[1])
            n_y1 = spline.degree * (spline.y[0] - spline.y[1])
            n_z1 = spline.degree *  (spline.z[0] - spline.z[1])
            norm = np.sqrt(n_x1 ** 2 + n_y1 ** 2 + n_z1 ** 2)
            norm_vec = 1.0 / norm * np.array([n_x1, n_y1, n_z1])
            vector_ids[vector_id] = [norm_vec[0], norm_vec[1], norm_vec[2]]
            vector_id += 1
            n_x1 = spline.degree * (spline.x[-1] - spline.x[-2])
            n_y1 = spline.degree * (spline.y[-1] - spline.y[-2])
            n_z1 = spline.degree * (spline.z[-1] - spline.z[-2])
            norm = np.sqrt(n_x1 ** 2 + n_y1 ** 2 + n_z1 ** 2)
            norm_vec = 1.0 / norm * np.array([n_x1, n_y1, n_z1])
            vector_ids[vector_id] = [norm_vec[0], norm_vec[1], norm_vec[2]]
            # Calculate spline and curve
            spline_id += 1
            spline_ids[spline_id] = [point_id -1, point_id, vector_id -1, vector_id]
            start_end_cross_section_correspondence[p_jun_start_id] = spline_id
            start_end_cross_section_correspondence[p_jun_end_id] = spline_id
            curve_id += 1
            curve_ids[curve_id] = [spline_id]
            # ---------- Cross section location start
            cut_times = beam.cut_times
            tck = [np.array(spline.t),
                   [np.array(spline.x), np.array(spline.y), np.array(spline.z)],
                   spline.degree]
            [x_coordinates, y_coordinates, z_coordinates] = interpolate.splev(cut_times, tck)
            [x_normals, y_normals, z_normals] = interpolate.splev(cut_times, tck, der=1)
            point_id += 1
            point_ids[point_id] = [x_coordinates[0], y_coordinates[0], z_coordinates[0]]
            # Cross section location end
            point_id += 1
            point_ids[point_id] = [x_coordinates[1], y_coordinates[1], z_coordinates[1]]
            p_c_start = point_id -1
            p_c_end = point_id

            # ----------- Cross section normal vector
            vector_id += 1
            vector_ids[vector_id] = [x_normals[0], y_normals[0], z_normals[0]]
            vector_id += 1
            vector_ids[vector_id] = [x_normals[1], y_normals[1], z_normals[1]]
            v_start = vector_id -1
            v_end = vector_id
            # Calculate beam
            beam_id += 1
            beam_id_list = []
            # Ad spline for beam
            beam_id_list.append(curve_id)
            # Add al valid cross section which are found
            # Calculate start cross sections
            if beam.crossSection1[0] != None:
                [xx, yy, zz] = beam.crossSection1[0]
                splines = []
                for id in range(len(xx)):
                    point_id += 1
                    point_ids[point_id] = [xx[id], yy[id], zz[id]]
                    if id == 0:
                        spline_start_point = point_id
                    if id != 0:
                        spline_id += 1
                        spline_ids[spline_id] = [point_id - 1, point_id]
                        splines.append(spline_id)
                    # Last point and close polygon
                    if id == len(xx) - 1:
                        spline_id += 1
                        spline_ids[spline_id] = [point_id, spline_start_point]
                        splines.append(spline_id)
                curve_id += 1
                curve_ids[curve_id] = splines
                beam_id_list.append(curve_id)
                cross_section_id += 1
                cross_sections_ids[cross_section_id] = [p_c_start, v_start, curve_id]
            # Calculate end cross sections
            if beam.crossSection2[0] != None:
                [xx, yy, zz] = beam.crossSection2[0]
                splines = []
                for id in range(len(xx)):
                    point_id += 1
                    point_ids[point_id] = [xx[id], yy[id], zz[id]]
                    if id == 0:
                        spline_start_point = point_id
                    if id != 0:
                        spline_id += 1
                        spline_ids[spline_id] = [point_id - 1, point_id]
                        splines.append(spline_id)
                    # Last point
                    if id == len(xx) - 1:
                        spline_id += 1
                        spline_ids[spline_id] = [point_id, spline_start_point]
                        splines.append(spline_id)
                curve_id += 1
                curve_ids[curve_id] = splines
                beam_id_list.append(curve_id)
                cross_section_id += 1
                cross_sections_ids[cross_section_id] = [p_c_end, v_end, curve_id]
            beam_ids[beam_id] = beam_id_list
            # Save the junction information
            end_marker = spline.end_connection_id
            start_marker = spline.start_connection_id
            if end_marker != None:
                if tuple(end_marker) in junction_connections:
                    junction_connections[tuple(end_marker)].append(cross_section_id)
                else:
                    junction_connections[tuple(end_marker)] = [cross_section_id]

                # Check if junction point is alreadcy set and then insert them
                if tuple(end_marker) in junction_id_point_list:
                    point_id_jun_end = junction_id_point_list[tuple(end_marker)] = point_id
                else:
                    point_id += 1
                    point_ids[point_id] = [end_marker[0], end_marker[1], end_marker[2]]
                    point_id_jun_end = point_id
                spline_id += 1
                spline_ids[spline_id] = [p_jun_end_id, point_id_jun_end]
                curve_id += 1
                curve_ids[curve_id] = spline_id
                # Create spline between junction and beam

            if start_marker != None:
                if tuple(start_marker) in junction_connections:
                    junction_connections[tuple(start_marker)].append(cross_section_id - 1)
                else:
                    junction_connections[tuple(start_marker)] = [cross_section_id - 1]
                    # Check if junction point is alreadcy set and then insert them

                    if tuple(start_marker) in junction_id_point_list:
                        point_id_jun_start = junction_id_point_list[tuple(start_marker)] = point_id
                    else:
                        point_id += 1
                        point_ids[point_id] = [start_marker[0], start_marker[1], start_marker[2]]
                        point_id_jun_start = point_id
                    spline_id += 1
                    spline_ids[spline_id] = [p_jun_start_id, point_id_jun_start]
                    curve_id += 1
                    curve_ids[curve_id] = spline_id
                    # Create spline between junction and beam

        file.write('POINT \n')
        for point_key in point_ids:
            if point_key in start_end_cross_section_correspondence:
                file.write(
                    f'{point_key}, {point_ids[point_key][0]}, {point_ids[point_key][1]}, {point_ids[point_key][2]},'
                    f' {start_end_cross_section_correspondence[point_key]} \n')
            else:
                file.write(f'{point_key}, {point_ids[point_key][0]}, {point_ids[point_key][1]}, {point_ids[point_key][2]} \n')
        file.write('ENDPOINT \n')

        file.write('VECTOR \n')
        for vector_key in vector_ids:
            file.write(f'{vector_key}, {vector_ids[vector_key][0]}, {vector_ids[vector_key][1]}, {vector_ids[vector_key][2]} \n')
        file.write('ENDVECTOR \n')

        file.write('SPLINE \n')
        for spline_key in spline_ids:
            if len(spline_ids[spline_key]) == 2:
                file.write(f'{spline_key}, {spline_ids[spline_key][0]}, {spline_ids[spline_key][1]} \n')
            else:
                file.write(
                    f'{spline_key}, {spline_ids[spline_key][0]}, {spline_ids[spline_key][1]}, {spline_ids[spline_key][2]}, {spline_ids[spline_key][3]} \n')
        file.write('ENDSPLINE \n')

        file.write('CURVE \n')
        for curve_key in curve_ids:
            spline_ids = curve_ids[curve_key]
            if type(spline_ids) == int:
                file.write(f'{curve_key}, {spline_ids}\n')
                continue
            if len(spline_ids) == 0: continue
            file.write(f'{curve_key}')
            for sp_id in spline_ids:
                file.write(f', {sp_id}')
            file.write("\n")
        file.write('ENDCURVE \n')

        file.write('SECTION \n')
        for cross_key in cross_sections_ids:
            file.write(f'{cross_key}, {cross_sections_ids[cross_key][0]}, {cross_sections_ids[cross_key][1]}, {cross_sections_ids[cross_key][2]}')
            file.write("\n")
        file.write('ENDSECTION \n')

        file.write('BEAM \n')
        for beam_key in beam_ids:
            file.write(f'{beam_key}')
            for beam_id_value in beam_ids[beam_key]:
                file.write(f', {beam_id_value}')
            file.write("\n")
        file.write('ENDBEAM \n')

        file.write('JUNCTION \n')
        junction_id = 0
        for junction_key, beam_ids in junction_connections.items():
            if  len(beam_ids) < 2:
                continue
            junction_id += 1
            file.write(f'{junction_id}')
            for cross_key in cross_sections_ids:
                for beam_id in beam_ids:
                    if beam_id == cross_key:
                        print(cross_key)
                        print(cross_sections_ids[cross_key][2])
                        file.write(f', {cross_sections_ids[cross_key][2]}')
            file.write("\n")
        file.write('ENDJUNCTION \n')
        file.close()
