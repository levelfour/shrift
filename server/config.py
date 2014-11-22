#!/usr/bin/env python
# coding: utf-8

import os
import datetime
import shutil

# Flask
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from flask import render_template
from flask import make_response
from werkzeug.utils import secure_filename

UPLOAD_DIR = os.path.abspath(os.path.dirname(__file__)) + '/file'
TRAIN_DATA_DIR = os.path.abspath(os.path.dirname(__file__)) + '/file/data/train-data'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.config['UPLOAD_DIR'] = UPLOAD_DIR
app.config['TRAIN_DATA_DIR'] = TRAIN_DATA_DIR
app.url_map.strict_slashes = False
app.debug = True

# MongoDB
from pymongo import MongoClient
from gridfs import GridFS

client = MongoClient('mongodb://localhost:27017')
db = client.shrift
fs = GridFS(db)
