from setuptools import setup, Extension
import os

# Check if Cython is available
try:
    from Cython.Build import cythonize
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False
    print("WARNING: Cython not installed. Cython extensions will not be compiled.")

source_file = "src/pythra/pythra/reconciler_cython.pyx"
extension_name = "pythra.pythra.reconciler_cython"

ext_modules = []

# Only attempt to compile if file exists and Cython is present
if CYTHON_AVAILABLE and os.path.exists(source_file):
    ext_modules = [
        Extension(
            name=extension_name,
            sources=[source_file],
            extra_compile_args=['-O3'] if os.name != 'nt' else ['/Ox'],
        ),
    ]

setup(
    # CRITICAL FIX: Tell setup.py that packages are in 'src'
    package_dir={'': 'src'},
    # ------------------------------------------------------
    ext_modules=cythonize(ext_modules, language_level="3") if ext_modules else [],
)