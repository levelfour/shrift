#!/usr/bin/env python
# coding: utf-8

import os
from config import *

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	return render_template('index.html', body="""
	<h1>Shrift OCR Engine Database</h1>
	""")

# recognize characters and return response
@app.route('/ocr', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
			import shrift
			return shrift.ocr(secure_filename(filename))

# upload train data for machine learning
@app.route('/upload', methods=['POST'])
def upload_train_data():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			name = secure_filename(file.filename)
			char = request.form['text']
			global fs
			fs.put(file, filename=name, text=char)
			return 'OK'

@app.route('/clear')
def clear():
	result = ""
	for (root, dirs, files) in os.walk(app.config['UPLOAD_DIR'], topdown=False):
		for f in files:
			if f != "empty":
				os.remove(os.path.join(app.config['UPLOAD_DIR'], f))
				result += f + '\n'
	return result 

if __name__ == '__main__':
	app.run(debug=True)
