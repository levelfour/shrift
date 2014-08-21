#!/usr/bin/env python
# coding: utf-8

import sys, os
import socket
from config import *
import shrift

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def scale(file):
	from werkzeug import FileStorage
	from PIL import Image
	from StringIO import StringIO
	from shrift import extract_sections
	import numpy as np
	im = Image.open(file).convert('L').resize((400, 400))
	a = np.asarray(im.point(lambda x: 1-x/255.))
	hsec = extract_sections(map(lambda x: np.mean(x), a))
	vsec = extract_sections(map(lambda x: np.mean(x), a.T))
	if len(hsec) > 1 or len(vsec) > 1:
		hsec = [hsec[0][0], hsec[-1][1]]
		vsec = [vsec[0][0], vsec[-1][1]]
	else:
		hsec = hsec[0]
		vsec = vsec[0]

	b = a[hsec[0]:hsec[1]]
	b = b.T[vsec[0]:vsec[1]].T
	new_im = Image.fromarray(b).resize((400, 400))
	new_im = new_im.point(lambda x: 255*(1-x))
	buf = StringIO()
	new_im.save(buf, 'jpeg')
	return buf.getvalue()

###############################
# main page (memo app)
###############################
@app.route('/')
def index():
	return render_template('index.html', body="""
	<canvas id="canvas" retina="true" width=1400 height=1600 style="border: solid"></canvas> 
	""")

###############################
# test page (train app)
###############################
@app.route('/test')
def test_index():
	return render_template('test.html', body="""
	<h1>Shrift OCR Engine Database</h1>
	""")

# display stored train data
@app.route('/data/<char>', methods=['GET'])
def show_data(char):
	import romkan
	global fs
	html = ""
	for f in fs.find({'filename': '{}.jpg'.format(char)}):
		html += "<img src='/image/{}' width=80 />".format(f.md5)
	
	if html == "":
		html = "<h2>no data...</h2>"

	return render_template('test.html', body=unicode("""
	<h1>Train Data for "{}"</h1>{}
	""".format(romkan.to_hiragana(char).encode('utf-8'), html), encoding='utf-8'))

# access to image by hash value(md5)
@app.route('/image/<hashv>', methods=['GET'])
def image_data(hashv):
	global fs
	objectid = fs.find({'md5': hashv})[0]._id
	response = make_response(fs.get(objectid).read())
	response.headers['Content-Type'] = 'image/jpeg'
	response.headers['Content-Disposition'] = 'attachment; filename={}.jpg'.format(hashv)
	return response

@app.route('/download/', methods=['GET'])
def make_train_data():
	import shrift
	shrift.generate_train_data()
	return render_template('test.html', body="""
	<h3>Generating train data...</h3>
	<div id="progress">
		<div id="loading"></div>
	</div>
	""")

@app.route('/add', methods=['GET'])
def make_canvas():
	return render_template('test.html', body="""
	<h3>draw character in canvas</h3>
	<canvas id="canvas" width=400 height=400 style="border: solid">
	</canvas> 
	<form id="canvas-form" action="/upload" method="post" encrypt="multipart/form-data">
		<div>
			<input id="text" type="text" name="text" placeHolder="target character" />
		</div>
		<button class="canvas btn-info" type="submit" id="send">Send</button>
		<button class="canvas btn-warning" id="clear">Clear</button>
	</form>
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
			file = scale(file)
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
	app.run(debug=True, host=socket.gethostbyname(socket.gethostname()))
