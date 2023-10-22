from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "A library for Epic Mickey modding."
LONG_DESCRIPTION = "A Python library for working with Epic Mickey's file structures and formats."

# Setting up
setup(
        name="epicmickeylib",
        version=VERSION,
        author="Ryan 'abso1utezer0' Koop",
        author_email="ryanckoop1@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            #"json",
            #"struct",
            #"io",
            #"sys",
            #"zlib"
        ], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'Epic Mickey', 'modding', 'video games'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
        ]
)