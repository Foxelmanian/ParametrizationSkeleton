from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from run import SkeletonBuilderController
import configparser
import os
import shutil


# 1.0 Folder and file paths as selection
master = Tk()
file_path = filedialog.askopenfilename(initialdir="/", title="Select STL file for skeleton model",
                                               filetypes=(("stl files", "*.stl"), ("all files", "*.*")))
cross_section_path = filedialog.askopenfilename(initialdir="/", title="Select STL file for cross section model",
                                           filetypes=(("stl files", "*.stl"), ("all files", "*.*")))
work_folder_path1 = filedialog.askdirectory(initialdir="/", title="Select work folder path")

no_design_space_path = filedialog.askopenfilename(initialdir="/", title="Select JSON file for user selection points",
                                           filetypes=(("Json File format", "*.JSON"), ("all files", "*.*")))


if cross_section_path == '':
    cross_section_path = file_path
# 2.0 Parameter file paths
Label(master, text="Software Developed by Munich University of Applied Sciences, 29.10.2019").grid(row=0, sticky=W)
Label(master, text="License Agreement LGPL-2.1 additional no distribution or commercialization withouth permission is allowed, usuage at your own risk. Usuage only for private tasks").grid(row=1, sticky=W)
Label(master, text="Publications of these results only under permission of Klemens Rother at the Munich University of Applied Sciences, we guarantee for no license compbillity to third party libaries").grid(row=2, sticky=W)


Label(master, text="Agreement by clicking Start skeletonize, disagree by clicking Quit").grid(row=3, sticky=W)

var1 = IntVar(value=1)
Checkbutton(master, text="Model is valid", variable=var1).grid(row=4, sticky=W)

var2 = IntVar()
Checkbutton(master, text="Robust closed beam line detection", variable=var2).grid(row=5, sticky=W)

var3 = IntVar()
Checkbutton(master, text="Coarse fast skeleton", variable=var3).grid(row=6, sticky=W)

var4 = IntVar(value=1)
Checkbutton(master, text="Center Spline along cross sections", variable=var4).grid(row=7, sticky=W)
# Voxel number
Label(master, text='Number of Voxels').grid(row=8, sticky=W)
v = StringVar(master, value='200')
entry_p1 = Entry(textvariable=v)
entry_p1.grid(row = 9,   stick = 'nsew')


v2 = StringVar(master, value='3')
Label(master, text='Radius deletion factor').grid(row=10, sticky=W)
entry_p2 = Entry(textvariable=v2)
entry_p2.grid(row = 11,   stick = 'nsew')


v3 = StringVar(master, value='5')
Label(master, text='Minimum number of chain points').grid(row=12, sticky=W)
entry_p3 = Entry(textvariable=v3)
entry_p3.grid(row = 13,   stick = 'nsew')



def var_states():
    messagebox.showinfo("Title", "workpath: " + work_folder_path1 + "\n" +
                                 "stl skeleton: " + file_path + "\n"+
                                 "stl crosssection: " + cross_section_path + "\n")
def skeletonize():
    config = configparser.ConfigParser()

    id = 0
    name_with_extension = os.path.basename(file_path)[0:-4]
    file_name = work_folder_path1 + '/config' + name_with_extension + str(id) + '.ini'
    while os.path.exists(file_name):
        id += 1
        file_name = work_folder_path1 + '/config' + name_with_extension + str(id) + '.ini'


    config['GENERAL'] = {'data_base_storage_path': work_folder_path1 + "/RunData" + name_with_extension}
    config['VOXELIZER'] = {'stl_path': file_path,
                           'number_of_voxels': int(entry_p1.get()),
                           'model_is_valid': bool(var1.get())}

    config['SKELETONIZER'] = {'detect_only_robust_closed_skeleton_lines': bool(var2.get()),
                              'coarse_skeletonization': bool(var3.get()),
                              'no_design_space_path': no_design_space_path}

    config['CLASSIFIER'] = {'delete_voxel_in_radius_around_branch_point': float(entry_p2.get())}

    config['CHAIN_BUILDER'] = {'minimum_number_of_voxels_in_a_chain': int(entry_p3.get())}



    config['BEAM_BUILDER'] = {'cross_section_stl_path': cross_section_path,
                              'origin_mesh_path': file_path,
                              'skele_file_export_path': work_folder_path1 + '/result' + name_with_extension + str(id) + '.skele',
                              'center_spline_along_cross_sections': var4.get()}

    config['Module'] = {'voxelizer': True,
                        'skeletonizer': True,
                        'classifier': True,
                        'chain_builder': True,
                        'beam_builder': True,
                        }
    if os.path.exists('config.ini'):
        os.remove('config.ini')

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    shutil.copy('config.ini', file_name)

    if os.path.exists(os.path.join(work_folder_path1 + name_with_extension)):
        shutil.rmtree(os.path.join(work_folder_path1 + name_with_extension))

    skeletonbuilder = SkeletonBuilderController()
    skeletonbuilder.run()

    if os.path.exists(work_folder_path1 + "/RunData"):
        shutil.rmtree(work_folder_path1 + "/RunData")

Button(master, text='Check choosen file paths', command=var_states).grid(row=14, sticky=W, pady=4)
Button(master, text='Start skeletonize', command=skeletonize).grid(row=15, sticky=W, pady=4)
Button(master, text='Quit', command=master.quit).grid(row=16, sticky=W, pady=4)
mainloop()
