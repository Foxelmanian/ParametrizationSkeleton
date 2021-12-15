from cx_Freeze import setup, Executable
import os
import shutil
import zipfile
import sys

print('Remove old build')
if os.path.exists('build'):
    shutil.rmtree('build')

os.environ['TCL_LIBRARY'] = r'C:\Users\AppData\Local\Programs\Python\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\AppData\Local\Programs\Python\Python36\tcl\tk8.6'
base = None
if sys.platform == "win32":
    base = "Win32GUI"

def build_model(model):

    additional_mods = ['tkinter', 'numpy.core._methods', 'numpy.lib.format', 'scipy.ndimage._ni_support', 'scipy.spatial.cKDTree', 'scipy.spatial.ckdtree',
                       'shapely.geometry', 'appdirs', 'packaging.version', 'traitsui.null.toolkit', 'pyface.ui.qt4.init']
    additional_packages = ['tkinter', 'scipy', 'numpy', 'trimesh',
                           'shapely', 'appdirs', 'packaging',
                           'mayavi', 'traitsui', 'pyface',
                           'tvtk', 'pygments']

    options = {
        'build_exe': {
            'packages': additional_packages,
            'includes': additional_mods,
            'include_files': [r"C:\Users\Denk\AppData\Local\Programs\Python\Python36\DLLs\tcl86t.dll",
                              r"C:\Users\Denk\AppData\Local\Programs\Python\Python36\DLLs\tk86t.dll"]
        }
    }

    #'scipy.ndimage._ni_support'
    setup(name='SkeletonBuilder',
          version='0.1',
          description='Transforms some part of a polygonmesh into a skeleton like structure as beam elements.',
          options = options,
          executables = [Executable(model + '.py', base=base)]
        )
exe_models = ['GUI']
for model in exe_models:
    build_model(model)

# Move binvox file to build folder
print("Move binvox executable to folder")
if not os.path.exists(os.path.join('build', 'exe.win-amd64-3.6', 'binvox.exe')):
    shutil.copy2("binvox.exe", os.path.join('build', 'exe.win-amd64-3.6'))
shutil.copy2("thinvox.exe", os.path.join('build', 'exe.win-amd64-3.6'))

# Extract the tvtk tool set
print("Extract tvtk to folder")
if not os.path.exists(os.path.join('build', 'exe.win-amd64-3.6', 'lib', 'tvtk', 'tvtk_classes')):
    zip_ref = zipfile.ZipFile(os.path.join('build', 'exe.win-amd64-3.6', 'lib', 'tvtk', 'tvtk_classes.zip'), 'r')
    zip_ref.extractall(os.path.join('build', 'exe.win-amd64-3.6', 'lib', 'tvtk'))
    zip_ref.close()

# Rename the scipy
print("rename Scipy ckdtree")
src_path = os.path.join('build', 'exe.win-amd64-3.6', 'lib', 'scipy', 'spatial', 'cKDTree.cp36-win_amd64.pyd')
dest_path = os.path.join('build', 'exe.win-amd64-3.6', 'lib', 'scipy', 'spatial', 'ckdtree.cp36-win_amd64.pyd')

if os.path.exists(src_path):
    os.rename(src_path, dest_path)
else:
    print("Scipy ckdttree file is not found")


print("Copy init file")
if not os.path.exists(os.path.join('build', 'exe.win-amd64-3.6', 'config.ini')):
    shutil.copy2("config.ini", os.path.join('build', 'exe.win-amd64-3.6'))


print("Finished")
#if not os.path.exists(os.path.join('build', 'exe.win-amd64-3.6', 'Data')):
#    shutil.copytree("Data", os.path.join('build', 'exe.win-amd64-3.6'))

