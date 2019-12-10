
from setuptools import setup, find_packages, Extension
import sys
import numpy
import os
import os.path as path
import multiprocessing

use_cython = True
include_cherab = False
force = False
profile = False

if "--skip-cython" in sys.argv:
    use_cython = False
    del sys.argv[sys.argv.index("--skip-cython")]

if "--include-cherab" in sys.argv:
    include_cherab = True
    del sys.argv[sys.argv.index("--include-cherab")]

if "--force" in sys.argv:
    force = True
    del sys.argv[sys.argv.index("--force")]

if "--profile" in sys.argv:
    profile = True
    del sys.argv[sys.argv.index("--profile")]

source_paths = ['vita']
compilation_includes = [".", numpy.get_include()]
compilation_args = []
cython_directives = {
    'language_level': 3
}
setup_path = path.dirname(path.abspath(__file__))

if use_cython:

    from Cython.Build import cythonize

    # build .pyx extension list
    extensions = []
    for package in source_paths:
        for root, dirs, files in os.walk(path.join(setup_path, package)):

            if os.path.split(root)[1] == "cherab" and not include_cherab:
                continue

            for file in files:
                if path.splitext(file)[1] == ".pyx":
                    pyx_file = path.relpath(path.join(root, file), setup_path)
                    module = path.splitext(pyx_file)[0].replace("/", ".")
                    extensions.append(Extension(module, [pyx_file], include_dirs=compilation_includes, extra_compile_args=compilation_args),)

    if profile:
        cython_directives["profile"] = True

    # generate .c files from .pyx
    extensions = cythonize(extensions, nthreads=multiprocessing.cpu_count(), force=force, compiler_directives=cython_directives)

else:

    # build .c extension list
    extensions = []
    for package in source_paths:
        for root, dirs, files in os.walk(path.join(setup_path, package)):
            for file in files:
                if path.splitext(file)[1] == ".c":
                    c_file = path.relpath(path.join(root, file), setup_path)
                    module = path.splitext(c_file)[0].replace("/", ".")
                    extensions.append(Extension(module, [c_file], include_dirs=compilation_includes, extra_compile_args=compilation_args),)

setup(
    name="vita",
    version="0.1",
    license="LGPL-2.1",
    namespace_packages=['vita'],
    description='The VITA particle and field tracing code for power load calculations',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics"
    ],
    install_requires=['numpy', 'cython>=0.28'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'vita_add_resource = vita.utility.scripts.add_resource:main',
            'vita_update_resource = vita.utility.scripts.update_resource:main',
            'vita_remove_resource = vita.utility.scripts.remove_resource:main',
            'vitarunner = vita.vitarunner:main'
        ]
    },
    include_package_data=True,
    zip_safe=False,
    ext_modules=extensions
)

