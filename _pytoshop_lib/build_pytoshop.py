"""
    This is a helper script executing the python executable with setup.py build_ext
    and some options to create compiled *.pyd inside this directory.

    As pip fails to compile Cython extension for pytoshop on some systems
    we try to build the extension our self.

    The actual build instructions are inside setup.py
"""
from shutil import rmtree
from pathlib import Path
from subprocess import call

# Compile and build Cython extension in current directory
build_dir = Path(__file__).parent

print('Build directory: ' + build_dir.as_posix())

build_cmd = f'python setup.py build_ext --build-lib {build_dir.as_posix()} --build-temp {build_dir.as_posix()}'
print('Executing: ' + build_cmd + '\n')

# Execute Python Extension build
result = call(build_cmd, cwd=build_dir)
print('\n###########\nBuild process ended with result ' + str(result) + '\n###########\n')

release_dir = Path('./Release')
if release_dir.exists():
    print('Cleaning up! Removing build-temp directory.')
    rmtree(release_dir)
