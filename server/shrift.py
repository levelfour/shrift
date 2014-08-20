#!/usr/bin/env python
# coding: utf-8

from config import *
import os, sys, re, datetime
import io
from PIL import Image
import pyocr
import pyocr.builders
import numpy as np
from sklearn import datasets

SVMLIGHT_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data')

label = [
	'a', 'i', 'u', 'e', 'o',
	'ka', 'ki', 'ku', 'ke', 'ko',
	'sa', 'si', 'su', 'se', 'so',
	'ta', 'ti', 'tu', 'te', 'to',
	'na', 'ni', 'nu', 'ne', 'no',
	'ha', 'hi', 'hu', 'he', 'ho',
	'ma', 'mi', 'mu', 'me', 'mo',
	'ya', 'yu', 'yo',
	'ra', 'ri', 'ru', 're', 'ro',
	'wa', 'wo', 'n'
]

# 手書き文字1文字から特徴ベクトルを生成する
# Algorithm:
#	ShriftTrainerは400*400の画像を返すので、グレースケール化して
#	10*10の小区画の平均をとり、1600次元の特徴ベクトルとする
# Vector: 40*40の1600次元濃淡ベクトル
# Class: 各文字と一対一対応した整数値
def extract(raw_str):
	img = Image.open(raw_str).convert('L')
	img = img.resize((400, 400))
	# グレースケール化した画像を行列にする
	# 白成分が多いので白黒を反転させる
	imarray = np.asarray(img.point(lambda x: 255 - x))
	# 各区画の濃淡の平均をとり特徴ベクトルとする
	return np.array([
		[imarray[10*i:10*(i+1),10*j:10*(j+1)].mean()
			for i in range(0, 40)
			for j in range(0, 40)
		]])

# データベースに格納されているtrain-dataから
# 学習用の特徴ベクトルを生成してsvmlight-formatで出力する
def generate_train_data():
	global fs, label
	data = None	# 特徴ベクトル
	target = []	# train-dataのクラス
	for f in fs.find():
		char, ext = os.path.splitext(f.filename)
		v = extract(io.BytesIO(f.read()))
		if data != None:
			data = np.r_[data, v]
		else:
			data = v
		target.append(char)

	target = map(lambda x: label.index(x), target)
	now = datetime.datetime.today()
	filename = os.path.join(
			SVMLIGHT_OUTPUT_PATH,
			'feature_{}{:0>2}{:0>2}{:0>2}{:0>2}.txt'.format(
				now.year, now.month, now.day, now.hour, now.minute))
	with open(filename, 'w') as f:
		datasets.dump_svmlight_file(data, target, f)

def ocr(filename):
    from sklearn.ensemble import RandomForestClassifier
	
    fpath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'file',
        filename)
    testX = extract(fpath)
    trainX, trainY = datasets.load_svmlight_file('data/feature_201408210039.txt', n_features=1600)
    clf = RandomForestClassifier()
    clf.fit(trainX.toarray(), trainY)
    return label[int(clf.predict(testX)[0])]

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
