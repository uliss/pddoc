#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

setup(name='pddoc',
      version='0.1',
      description='PureData documentation tools',
      classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Topic :: Software Development :: Documentation',
            'Topic :: Multimedia :: Sound/Audio',
            'Programming Language :: Python :: 2.7',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
      ],
      url='https://github.com/uliss/pddoc',
      author='Serge Poltavski',
      author_email='serge.poltavski@gmail.com',
      keywords='puredata documentation',
      license='GPLv3',
      packages=['pddoc'],
      install_requires=[
            'termcolor', 'colorama'
      ],
      zip_safe=False)
