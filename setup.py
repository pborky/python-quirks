#!/usr/bin/env python

from distutils.core import setup

setup(name='Python Quirks',
      version='0.1',
      description='Small and handy python routines',
      author='Peter Boraros',
      author_email='pborky@pborky.sk',
      url='https://github.com/pborky/python-quirks',
      packages=['quirks',],
      requires=['fabulous', 'tables (==2.3.1)',],
      install_requires=['fabulous',], 
     )
