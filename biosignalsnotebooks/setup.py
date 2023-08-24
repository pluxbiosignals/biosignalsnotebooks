"""
File that specifies package requisites for a correct functioning of all available functions.

"""

from setuptools import setup
from os import path
from sys import platform

# Adjust requirements accordingly to the operating system.
requirements = ['numpy==1.22.2', 'matplotlib', 'scipy==1.8.1', 'h5py', 'wget', 'datetime', 'bokeh==2.4.3', 'scipy', 'IPython',
                'pandas', 'nbformat', 'ipython', 'requests', 'python-magic;platform_system=="Linux"',
                'python-magic-bin;platform_system!="Linux"', 'libmagic']

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README_BSNB.md'), encoding='utf-8') as f:
      long_description = f.read()


setup(name='biosignalsnotebooks',
      version='0.6.13',#major.minor.build_nbr
      description='A Python package for supporting the external loading and processing of '
                  'OpenSignals electrophysiological acquisitions.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/biosignalsplux/biosignalsnotebooks',
      author='PLUX Wireless Biosignals',
      author_email='gramos@plux.info',
      license='MIT',
      packages=['biosignalsnotebooks'],
      platforms=["win32", "darwin", "os2", "os2emx"],
      setup_requires=['numpy'],
      install_requires=requirements,
      zip_safe=False,
      include_package_data=True)

# 02/11/2018  17h33m :)
