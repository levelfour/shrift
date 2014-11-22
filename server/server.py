#!/usr/bin/env python
# coding: utf-8

import sys, os, re
import socket
from config import *
import shrift

# convert illegal filename (ex. including '/') to legal filename
def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# extract one character from canvas -> scaling
def scale(file):
	from werkzeug import FileStorage
	from PIL import Image
	from StringIO import StringIO
	from shrift import extract_lines
	from shrift import extract_characters
	import numpy as np
	# resize image
	im = Image.open(file).convert('L').resize((400, 400))
	# convert image to binary data
	a = np.asarray(im.point(lambda x: 1-x/255.))
	# extract character section
	hsec = extract_lines(map(lambda x: np.mean(x), a))
	vsec = extract_characters(map(lambda x: np.mean(x), a.T))
	if len(hsec) > 1 or len(vsec) > 1:
		# if there are multiple sections -> join to one section
		hsec = [hsec[0][0], hsec[-1][1]]
		vsec = [vsec[0][0], vsec[-1][1]]
	else:
		hsec = hsec[0]
		vsec = vsec[0]

	# extract necessary part from binary data
	b = a[hsec[0]:hsec[1]]
	b = b.T[vsec[0]:vsec[1]].T
	new_im = Image.fromarray(b).resize((400, 400))
	new_im = new_im.point(lambda x: 255*(1-x))
	# output as jpeg image
	buf = StringIO()
	new_im.save(buf, 'jpeg')
	return buf.getvalue()

###############################
# main page (memo app)
###############################
@app.route('/')
def index():
	with open('templates/app.html', 'r') as f:
		html = f.read()
	return render_template('index.html', body=html)

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
		html += """
		<a class="delete-img" data-target="{}" href="#">
			<img src='/image/{}' width=80 />
		</a>
		""".format(f.md5, f.md5)
	
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

# delete image by hash value(md5)
@app.route('/delete/<hashv>', methods=['GET'])
def delete_data(hashv):
	global fs
	objectid = fs.find({'md5': hashv})[0]._id
	fs.delete(objectid)
	return 'OK'

@app.route('/download/', methods=['GET'])
def make_train_data():
	import shrift
	shrift.generate_train_data()
	with open('templates/download.html', 'r') as f:
		html = f.read()
	return render_template('test.html', body=html)

@app.route('/add', methods=['GET'])
def make_canvas():
	with open('templates/add.html', 'r') as f:
		html = f.read()
	return render_template('test.html', body=html)

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
@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'GET':
		with open('templates/upload.html', 'r') as f:
			html = f.read()
		return render_template('test.html', body=html)
	elif request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			name = secure_filename(file.filename)
			char = request.form['text']
			if re.split("\.", name)[0] != char:
				# name format: <target-char>.jpg
				name = "{}.jpg".format(char)
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
	app.run(debug=True, host=socket.gethostbyname(socket.gethostname()), port=int(sys.argv[1]))
