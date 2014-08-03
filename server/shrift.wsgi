#!/usr/bin/env python
# coding: utf-8

import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from server import app
application = app
