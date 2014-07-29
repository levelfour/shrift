#!/usr/bin/env python
# coding: utf-8

import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/file'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.url_map.strict_slashes = False
app.debug = True

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	return 'Shrift'

@app.route('/upload', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			import shrift
			return shrift.ocr(secure_filename(filename))

@app.route('/clear')
def clear():
	result = ""
	for (root, dirs, files) in os.walk(UPLOAD_FOLDER, topdown=False):
		for f in files:
			if f != "empty":
				os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))
				result += f + '\n'
	return result 

if __name__ == '__main__':
	app.run(debug=True)
