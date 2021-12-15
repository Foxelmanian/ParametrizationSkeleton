import numpy as np
from enum import Enum
class MedialAxisThinning(object):


    def __init__(self, preserve_only_homotopy=True, check_curve_end_point_sequentiell=False):

        # Parameters for skeleton creations
        self.__preserve_only_homotopy = preserve_only_homotopy
        self.__check_curve_end_point_sequentiell = check_curve_end_point_sequentiell

        self.__no_design_space = [[],[],[]]
        self.__octant_index_table = {1: [(0), (1, 2), (3, 3), (9, 5), (4, (2, 3, 4)), (10, (2, 5, 6)), (12, (3, 5, 7))],
                                     2: [(2), (1, 1), (5, 4), (11, 6), (4, (1, 3, 4)), (10, (1, 5, 6)), (13, (4, 6, 8))],
                                     3: [(6), (3, 1), (7, 4), (14, 7), (4, (1, 2, 4)), (12, (1, 5, 7)), (15, (4, 7, 8))],
                                     4: [(8), (5, 2), (7, 3), (16, 8), (4, (1, 2, 3)), (13, (2, 6, 8)), (15, (3, 7, 8))],
                                     5: [(17), (9, 1), (18, 6), (20, 7), (10, (1, 2, 6)), (12, (1, 3, 7)), (21, (6, 7, 8))],
                                     6: [(19), (11, 2), (18, 5), (22, 8), (10, (1, 2, 5)), (13, (2, 4, 8)),
                                         (21, (5, 7, 8))],
                                     7: [(23), (14, 3), (20, 5), (24, 8), (12, (1, 3, 5)), (15, (3, 4, 8)),
                                         (21, (5, 6, 8))],
                                     8: [(25), (16, 4), (22, 6), (24, 7), (13, (2, 4, 6)), (15, (3, 4, 7)),
                                         (21, (5, 6, 7))]}
        self.__euler_table = get_euler_table()

    def set_no_design_space(self, no_x, no_y, no_z):
        self.__no_design_space = (no_x, no_y, no_z)

    def reset_no_design_space(self):
        self.__no_design_space =([],[],[])

    def run(self, data):
        skeleton = self.__create_skeleton(data)
        return skeleton


    def __create_skeleton(self, data):
        print('Create Skeleton via Lee94')
        iteration = 0
        skel = np.pad(data, (1), 'constant')
        skel = skel.astype(int)
        x_size = len(skel)
        y_size = len(skel[0])
        z_size = len(skel[0][0])

        unchangedBorders = 0
        no_design_tree = {}
        for x in range(x_size + 1):
            for y in range(y_size + 1):
                for z in range(z_size + 1):
                    no_design_tree[(x, y, z)] = False

        # Select no design space if specified
        x_no, y_no, z_no = self.__no_design_space
        for x_n, y_n, z_n in zip(x_no, y_no, z_no): no_design_tree[(x_n, y_n, z_n)] = True

        while (unchangedBorders < 6):
            unchangedBorders = 0
            if unchangedBorders == 6:
                print('Run Again for Surface points')
                unchangedBorders = 0
                save_sufrace_points = True
            for currentBorder in range(1, 7):
                iteration += 1
                cands = np.zeros((x_size, y_size, z_size), dtype=bool)
                if currentBorder == 1:
                    y = np.array(list(range(1, y_size)))
                    cands[:, y, :] = skel[:, y, :] - skel[:, y - 1, :]

                elif currentBorder == 2:
                    y = np.array(list(range(0, y_size - 1)))
                    cands[:, y, :] = skel[:, y, :] - skel[:, y + 1, :]

                elif currentBorder == 4:
                    x = np.array(list(range(1, x_size)))
                    cands[x, :, :] = skel[x, :, :] - skel[x - 1, :, :]
                elif currentBorder == 3:
                    x = np.array(list(range(0, x_size - 1)))
                    cands[x, :, :] = skel[x, :, :] - skel[x + 1, :, :]

                elif currentBorder == 6:
                    z = np.array(list(range(1, z_size)))
                    cands[:, :, z] = skel[:, :, z] - skel[:, :, z - 1]
                elif currentBorder == 5:
                    z = np.array(list(range(0, z_size - 1)))
                    cands[:, :, z] = skel[:, :, z] - skel[:, :, z + 1]

                noChange = True
                # All true values will be deleted
                # -------------- Condition 0: Choose border voxel
                cands = np.logical_and(skel, cands)
                cands = np.argwhere(cands != 0)
                if not np.any(cands): unchangedBorders += 1; continue
                x, y, z = cands[:, 0], cands[:, 1], cands[:, 2]
                nhood = self.__get_neighbour(skel, cands)
                true_vec_delete_voxel = np.ones(len(x)).astype(bool)

                # print(f' #-1 truvec {len(true_vec_delete_voxel)}, x {len(x)}')
                # --------------- Condition 1: End points and homotpy:
                if not self.__preserve_only_homotopy:
                    # Check is if there are two only two neighbour --> Yes dont use this point

                    true_vec_delete_voxel = np.isin(np.sum(nhood, 1), 2, invert=True)

                    [nhood, x, y, z, true_vec_delete_voxel] = nhood[true_vec_delete_voxel], x[true_vec_delete_voxel], y[true_vec_delete_voxel], \
                                       z[true_vec_delete_voxel], true_vec_delete_voxel[true_vec_delete_voxel]
                    if not np.any(true_vec_delete_voxel): unchangedBorders += 1; continue

                # -------------- Condition 2: Use only euler Invariant points
                true_vec_delete_voxel = self.__euler_number_is_invariant(nhood)
                [nhood, x, y, z, true_vec_delete_voxel] = nhood[true_vec_delete_voxel], x[true_vec_delete_voxel], y[true_vec_delete_voxel], \
                                                          z[true_vec_delete_voxel], true_vec_delete_voxel[true_vec_delete_voxel]
                if not np.any(true_vec_delete_voxel): unchangedBorders += 1; continue


                # --------------- Condition 4: Use only simple voxels
                true_vec_delete_voxel = self.__is_simple(nhood)
                [nhood, x, y, z, true_vec_delete_voxel] = nhood[true_vec_delete_voxel], x[true_vec_delete_voxel], y[true_vec_delete_voxel], z[
                    true_vec_delete_voxel], true_vec_delete_voxel[true_vec_delete_voxel]
                if not np.any(true_vec_delete_voxel): unchangedBorders += 1; continue

                # --------------- Condition 5: No Design Space
                for vec_id, (xx, yy, zz) in enumerate(zip(x, y, z)):
                    if no_design_tree[(xx - 1, yy - 1, zz - 1)]: true_vec_delete_voxel[vec_id] = False
                [nhood, x, y, z, true_vec_delete_voxel] = nhood[true_vec_delete_voxel], x[true_vec_delete_voxel], \
                                   y[true_vec_delete_voxel], z[true_vec_delete_voxel], \
                                    true_vec_delete_voxel[true_vec_delete_voxel]
                if not np.any(true_vec_delete_voxel): unchangedBorders += 1; continue

                # -------------- Recheck simple points

                # print(f'C6 Recheck Simple points {len(true_vec_delete_voxel)}')
                iList = []
                # Modolo operator
                x1 = np.array(np.mod(x + 1, 2), 'bool')
                y1 = np.array(np.mod(y + 1, 2), 'bool')
                z1 = np.array(np.mod(z + 1, 2), 'bool')
                x2 = np.invert(x1)
                y2 = np.invert(y1)
                z2 = np.invert(z1)
                iList.append(np.logical_and(np.logical_and(x1, y1), z1))
                iList.append(np.logical_and(np.logical_and(x2, y1), z1))
                iList.append(np.logical_and(np.logical_and(x1, y2), z1))
                iList.append(np.logical_and(np.logical_and(x2, y2), z1))
                iList.append(np.logical_and(np.logical_and(x1, y1), z2))
                iList.append(np.logical_and(np.logical_and(x2, y1), z2))
                iList.append(np.logical_and(np.logical_and(x1, y2), z2))
                iList.append(np.logical_and(np.logical_and(x2, y2), z2))
                # print('#-------------------------')

                for ii in range(8):
                    if np.sum(iList[ii]) != 0:
                        idx = np.where(iList[ii] == True)[0]
                        # Remove point from skeleton
                        cands = []
                        for id in idx: skel[x[id], y[id], z[id]] = False; cands.append([x[id], y[id], z[id]])

                        cands = np.array(cands)
                        nh = self.__get_neighbour(skel, cands)
                        # true_vec_simple_multiple = np.invert(self.__is_simple(nh))

                        true_vec_simple_multiple = np.invert(self.__is_simple(nh))
                        true_vec_euler_inv_multiple = np.invert((self.__euler_number_is_invariant(nh)))
                        idx_rc_simp = np.where(true_vec_simple_multiple == True)[0]
                        idx_rc_euler = np.where(true_vec_euler_inv_multiple == True)[0]
                        noSingleChangeIsFound = True

                        # print(f'------ Candidates Point {cands}')
                        if len(idx_rc_simp > 0):
                            for id in idx_rc_simp:
                                xr, yr, zr = cands[id, 0], cands[id, 1] , cands[id, 2]
                                skel[xr, yr, zr] = 1
                                noSingleChangeIsFound = False

                        if len(idx_rc_euler > 0):
                            for id in idx_rc_euler:
                                xr, yr, zr = cands[id, 0], cands[id, 1], cands[id, 2]
                                skel[xr, yr, zr] = 1
                                noSingleChangeIsFound = False

                        if not self.__preserve_only_homotopy and self.__check_curve_end_point_sequentiell:
                            true_vec_neighbour_multiple = np.invert((np.isin(np.sum(nh, 1), 2, invert=True)))
                            idx_rc_neighbour = np.where(true_vec_neighbour_multiple == True)[0]
                            if len(idx_rc_neighbour > 0):
                                for id in idx_rc_neighbour:
                                    xr, yr, zr = cands[id, 0], cands[id, 1], cands[id, 2]
                                    skel[xr, yr, zr] = 1
                                    # print(f'End Point {xr, yr, zr}')
                                    noSingleChangeIsFound = False


                        if noSingleChangeIsFound:
                            noChange = False

                if noChange:
                    print(unchangedBorders, 'No Change')
                    unchangedBorders += 1


        return skel[1:x_size - 1, 1:y_size - 1, 1:z_size - 1 ]

    def __is_simple(self, N):
        n_size = len(N)
        is_simple = np.ones(n_size, bool)
        cube = np.zeros((n_size, 26), int)
        cube[:, 0:13] = N[:, 0:13]
        cube[:, 13:26] = N[:, 14:27]
        label = 2 * np.ones(n_size, int)
        for i in range(26):
            idx = np.where(np.logical_and(cube[:, i] == 1, is_simple))
            if len(idx[0]) > 0:
                tmp_label = label[idx]
                if i in [0, 1, 3, 4, 9, 10, 12]:
                    cube[idx, :] = self.__get_octant_label(1, tmp_label, cube[idx, :][0])
                elif i in [2, 5, 11, 13]:
                    cube[idx, :] = self.__get_octant_label(2, tmp_label, cube[idx, :][0])
                elif i in [6, 7, 14, 15]:
                    cube[idx, :] = self.__get_octant_label(3, tmp_label, cube[idx, :][0])
                elif i in [8, 16]:
                    cube[idx, :] = self.__get_octant_label(4, tmp_label, cube[idx, :][0])
                elif i in [17, 18, 20, 21]:
                    cube[idx, :] = self.__get_octant_label(5, tmp_label, cube[idx, :][0])
                elif i in [19, 22]:
                    cube[idx, :] = self.__get_octant_label(6, tmp_label, cube[idx, :][0])
                elif i in [23, 24]:
                    cube[idx, :] = self.__get_octant_label(7, tmp_label, cube[idx, :][0])
                elif i in [25]:
                    cube[idx, :] = self.__get_octant_label(8, tmp_label, cube[idx, :][0])
                label[idx] = label[idx] + 1
                del_idx = np.greater(label, 3)
                index_delete = np.where(label > 3)
                if np.sum(del_idx) > 0:
                    is_simple[index_delete] = False
        return is_simple

    def __single_octant_recursion(self, rec_tuple, label, cube):
        idx = np.where(cube[:, rec_tuple[0]] == 1)[0]
        if len(idx) > 0:
            cube[idx, rec_tuple[0]] = label[idx]
            cube[idx, :] = self.__get_octant_label(rec_tuple[1], label[idx], cube[idx, :])
        return cube

    def __tri_octant_recursion(self, rec_tuple, label, cube):

        index_1_rec = rec_tuple[1][0]
        index_2_rec = rec_tuple[1][1]
        index_3_rec = rec_tuple[1][2]
        idx = np.where(cube[:, rec_tuple[0]] == 1)[0]
        if len(idx) > 0:
            cube[idx, rec_tuple[0]] = label[idx]
            cube[idx, :] = self.__get_octant_label(index_1_rec, label[idx], cube[idx, :])
            cube[idx, :] = self.__get_octant_label(index_2_rec, label[idx], cube[idx, :])
            cube[idx, :] = self.__get_octant_label(index_3_rec, label[idx], cube[idx, :])
        return cube

    def __get_octant_label(self, octant, label, cube):
        octant_index_tuble = self.__octant_index_table[octant]
        no_recur_index = octant_index_tuble[0]
        rec_tuple_1 = octant_index_tuble[1]
        rec_tuple_2 = octant_index_tuble[2]
        rec_tuple_3 = octant_index_tuble[3]
        rec_tuple_4 = octant_index_tuble[4]
        rec_tuple_5 = octant_index_tuble[5]
        rec_tuple_6 = octant_index_tuble[6]

        if octant <= 8 and octant >= 1:
            # No recursion is needed
            idx = np.where(cube[:, no_recur_index] == 1)[0]
            if len(idx) > 0:
                cube[idx, no_recur_index] = label[idx]

            # three times only one time recursion
            cube = self.__single_octant_recursion(rec_tuple_1, label, cube)
            cube = self.__single_octant_recursion(rec_tuple_2, label, cube)
            cube = self.__single_octant_recursion(rec_tuple_3, label, cube)

            # three times tri time recursion
            cube = self.__tri_octant_recursion(rec_tuple_4, label, cube)
            cube = self.__tri_octant_recursion(rec_tuple_5, label, cube)
            cube = self.__tri_octant_recursion(rec_tuple_6, label, cube)
        return cube

    def int_to_binary(self, value):
        print("{0:b}".format(value))


    def __euler_number_is_invariant(self, nhood):
        """ In this module the euler invariant is calculated by using octants

        :param nhood: Array of Neighbourhood of the current voxel
        :return: Array of boolean of euler invariant points
        """
        eulerChar = np.zeros(len(nhood), int)
        # Go through all directions north west, east west
        for octant_direction in OctantDirection.__members__.values():
            eulerChar += self.__euler_table[self.__get_octan_direction(nhood, octant_direction.value)]
        eulerInv = np.zeros(len(eulerChar), bool)
        eulerInv[np.where(eulerChar == 0)] = True
        return eulerInv

    def __get_octan_direction(self, img, octant_direction_values):
        """ Get all neighbours in the octant direction --> set them true

        :param img: 3D image of the model
        :param octant_direction_value: Index of
        :return:
        """
        table = [128, 64, 32, 16, 8, 4, 2]
        n = np.ones(len(img), int)
        for octant_direction_value, table_label in zip(octant_direction_values, table):
            n[np.argwhere(img[:, octant_direction_value] == 1)] = \
                np.bitwise_or(n[np.argwhere(img[:, octant_direction_value] == 1)], table_label)
        return n

    def __get_neighbour(self, skel, cands):
        """ Get the neighbour of the voxel candidates

        :param skel: 3D Voxel current skeleton structure
        :param cands: Current Voxel candidates
        :return: Neighbourhood of the voxel as id
        """
        x = cands[:, 0]
        y = cands[:, 1]
        z = cands[:, 2]
        nhood = np.zeros((len(cands), 27), bool)  # 27 cases
        for xx in range(3):
            for yy in range(3):
                for zz in range(3):
                    w = xx + 3 * yy + 3 * 3 * zz
                    xn = x + xx - 1
                    yn = y + yy - 1
                    zn = z + zz - 1
                    nhood[:, w] = skel[xn, yn, zn]
        return nhood


class OctantDirection(Enum):
    SWU = [24, 25, 15, 16, 21, 22, 12]
    SEU = [26, 23, 17, 14, 25, 22, 16]
    NWU = [18, 21, 9, 12, 19, 22, 10]
    NEU = [20, 23, 19, 22, 11, 14, 10]
    SWB = [6, 15, 7, 16, 3, 12, 4]
    SEB = [8, 7, 17, 16, 5, 4, 14]
    NWB = [0, 9, 3, 12, 1, 10, 4]
    NEB = [2, 1, 11, 10, 5, 4, 14]


def get_euler_table():
    LUT = np.zeros(256, int)
    LUT[1] = 1
    LUT[3] = -1
    LUT[5] = -1
    LUT[7] = 1
    LUT[9] = -3
    LUT[11] = -1
    LUT[13] = -1
    LUT[15] = 1
    LUT[17] = -1
    LUT[19] = 1
    LUT[21] = 1
    LUT[23] = -1
    LUT[25] = 3
    LUT[27] = 1
    LUT[29] = 1
    LUT[31] = -1
    LUT[33] = -3
    LUT[35] = -1
    LUT[37] = 3
    LUT[39] = 1
    LUT[41] = 1
    LUT[43] = -1
    LUT[45] = 3
    LUT[47] = 1
    LUT[49] = -1
    LUT[51] = 1
    LUT[53] = 1
    LUT[55] = -1
    LUT[57] = 3
    LUT[59] = 1
    LUT[61] = 1
    LUT[63] = -1
    LUT[65] = -3
    LUT[67] = 3
    LUT[69] = -1
    LUT[71] = 1
    LUT[73] = 1
    LUT[75] = 3
    LUT[77] = -1
    LUT[79] = 1
    LUT[81] = -1
    LUT[83] = 1
    LUT[85] = 1
    LUT[87] = -1
    LUT[89] = 3
    LUT[91] = 1
    LUT[93] = 1
    LUT[95] = -1
    LUT[97] = 1
    LUT[99] = 3
    LUT[101] = 3
    LUT[103] = 1
    LUT[105] = 5
    LUT[107] = 3
    LUT[109] = 3
    LUT[111] = 1
    LUT[113] = -1
    LUT[115] = 1
    LUT[117] = 1
    LUT[119] = -1
    LUT[121] = 3
    LUT[123] = 1
    LUT[125] = 1
    LUT[127] = -1
    LUT[129] = -7
    LUT[131] = -1
    LUT[133] = -1
    LUT[135] = 1
    LUT[137] = -3
    LUT[139] = -1
    LUT[141] = -1
    LUT[143] = 1
    LUT[145] = -1
    LUT[147] = 1
    LUT[149] = 1
    LUT[151] = -1
    LUT[153] = 3
    LUT[155] = 1
    LUT[157] = 1
    LUT[159] = -1
    LUT[161] = -3
    LUT[163] = -1
    LUT[165] = 3
    LUT[167] = 1
    LUT[169] = 1
    LUT[171] = -1
    LUT[173] = 3
    LUT[175] = 1
    LUT[177] = -1
    LUT[179] = 1
    LUT[181] = 1
    LUT[183] = -1
    LUT[185] = 3
    LUT[187] = 1
    LUT[189] = 1
    LUT[191] = -1
    LUT[193] = -3
    LUT[195] = 3
    LUT[197] = -1
    LUT[199] = 1
    LUT[201] = 1
    LUT[203] = 3
    LUT[205] = -1
    LUT[207] = 1
    LUT[209] = -1
    LUT[211] = 1
    LUT[213] = 1
    LUT[215] = -1
    LUT[217] = 3
    LUT[219] = 1
    LUT[221] = 1
    LUT[223] = -1
    LUT[225] = 1
    LUT[227] = 3
    LUT[229] = 3
    LUT[231] = 1
    LUT[233] = 5
    LUT[235] = 3
    LUT[237] = 3
    LUT[239] = 1
    LUT[241] = -1
    LUT[243] = 1
    LUT[245] = 1
    LUT[247] = -1
    LUT[249] = 3
    LUT[251] = 1
    LUT[253] = 1
    LUT[255] = -1
    return LUT