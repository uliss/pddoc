#!/usr/bin/env python
# coding=utf-8

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='pddoc',
      version='0.1.4',
      description='PureData documentation tools',
      long_description=readme(),
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
          'termcolor', 'colorama', 'six', 'mako', 'argparse'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
          'console_scripts': ['pd2image=pddoc.pd2image:main']
      },
      include_package_data=True,
      zip_safe=False)
