#!/usr/bin/env python
# coding: utf-8

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("shrift", ["shrift.py"])]

setup(
  name = 'Shrift OCR Engine',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
