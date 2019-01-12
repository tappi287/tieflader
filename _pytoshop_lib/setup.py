"""
    As pip fails to compile Cython extension for pytoshop on some systems
    we try to build the extension our self.
"""
from pathlib import Path
from distutils.core import setup
from Cython.Build import cythonize

import pytoshop

module_file = 'packbits.pyx'
pytoshop_path = Path(pytoshop.__path__[0])
extension_modules_path = pytoshop_path / module_file

setup(
    ext_modules=cythonize(extension_modules_path.as_posix())
)