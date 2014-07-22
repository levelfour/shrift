#!/usr/bin/env python
# coding: utf-8

import sys, re
from PIL import Image
import pyocr
import pyocr.builders

if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise RuntimeError('too few args')

	srcname = sys.argv[1]
	re_ext = r'(.[A-Za-z]+)$'
	r = re.compile(re_ext)
	ext = r.search(srcname).group(0)
	binname = re.sub(re_ext, '_bin'+ext, srcname)

	# 画像をグレースケールで読み込む
	src_image = Image.open(srcname).convert("L")

	# グレースケール画像を2値化
	bin_image = src_image.point(
			lambda col: 255 if col > 180 else 0
			)

	# 2値化された画像を保存
	bin_image.save(binname)

	tools = pyocr.get_available_tools()
	tool = tools[0]
	lang = 'eng'

	txt = tool.image_to_string(
			Image.open(binname),
			lang=lang,
			builder=pyocr.builders.TextBuilder())
	print txt
