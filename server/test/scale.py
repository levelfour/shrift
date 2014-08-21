#!/usr/bin/env python
# coding: utf-8

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
from shrift import extract_sections
from config import *
from PIL import Image
from StringIO import StringIO
import numpy as np

SIZE = 400

if __name__ == '__main__':
	global fs
	for f in fs.find():
		im = Image.open(io.BytesIO(f.read())).convert('L').resize((SIZE, SIZE))
		a = np.asarray(im.point(lambda x: 1-x/255.))
		hsec = extract_sections(map(lambda x: np.mean(x), a))
		vsec = extract_sections(map(lambda x: np.mean(x), a.T))
		if len(hsec) > 1 or len(vsec) > 1:
			print('something wrong with image')
			continue
		else:
			hsec = hsec[0]
			vsec = vsec[0]

		b = a[hsec[0]:hsec[1]]
		b = b.T[vsec[0]:vsec[1]].T
		new_im = Image.fromarray(b)
		new_im = new_im.point(lambda x: 255*(1-x))
		raw = StringIO()
		new_im.save(raw, 'jpeg')
		fs.put(raw.getvalue(), filename=f.filename, text=f.text)
		fs.delete(f._id)
