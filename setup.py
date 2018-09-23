#!/usr/bin/env python3
# coding=utf-8

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='pddoc',
      version='0.5.3',
      description='PureData documentation tools',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Topic :: Software Development :: Documentation',
          'Topic :: Multimedia :: Sound/Audio',
          'Programming Language :: Python :: 3.3',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
      ],
      url='https://github.com/uliss/pddoc',
      author='Serge Poltavski',
      author_email='serge.poltavski@gmail.com',
      keywords='puredata documentation',
      license='GPLv3',
      packages=['pddoc', 'pddoc.bin', 'pddoc.pd', 'pddoc.txt'],
      install_requires=[
          'termcolor', 'colorama', 'six', 'mako', 'argparse', 'lxml', 'ply', 'docutils', 'sphinx'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
          'console_scripts': ['pd_pd2img   = pddoc.bin.pd_pd2img:main',
                              'pd_obj2img  = pddoc.bin.pd_obj2img:main',
                              'pd_doc2html = pddoc.bin.pd_doc2html:main',
                              'pd_doc2pd   = pddoc.bin.pd_doc2pd:main',
                              'pd_ascii2pd = pddoc.bin.pd_ascii2pd:main',
                              'pd_makelibrary = pddoc.bin.pd_makelibrary:main',
                              'pd_lib2pd   = pddoc.bin.pd_lib2pd:main',
                              'pd_cat2pd   = pddoc.bin.pd_cat2pd:main']
      },
      include_package_data=True,
      zip_safe=False)
