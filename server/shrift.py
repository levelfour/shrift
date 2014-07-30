#!/usr/bin/env python
# coding: utf-8

import os, sys, re
from PIL import Image
import pyocr
import pyocr.builders

def ocr(filename):
	fpath = os.path.join(
			os.path.abspath(os.path.dirname(__file__)),
			'file',
			filename)
	return recognize(fpath)

def recognize(filename, binarize=False):
	re_ext = r'(.[A-Za-z]+)$'
	r = re.compile(re_ext)
	ext = r.search(filename).group(0)

	if binarize:
		# 画像をグレースケールで読み込む
		src_image = Image.open(filename).convert("L")

		# グレースケール画像を2値化
		bin_image = src_image.point(
				lambda col: 255 if col > 180 else 0)

		# 2値化された画像を保存
		filename = re.sub(re_ext, '_bin'+ext, filename)
		bin_image.save(filename)

	tools = pyocr.get_available_tools()
	tool = tools[0]
	lang = 'eng'

	txt = tool.image_to_string(
			Image.open(filename),
			lang=lang,
			builder=pyocr.builders.TextBuilder())
	return txt

if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise RuntimeError('too few args')

	srcname = sys.argv[1]
	print ocr(srcname)
