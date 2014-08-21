#!/usr/bin/env python
# coding: utf-8

from config import *
import os, sys, re, datetime
import io
import glob
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
def encode(raw_str="", raw=None):
	img = raw
	if img is None:
		img = Image.open(raw_str).convert('L')

	img = img.resize((400, 400))

	# グレースケール化した画像を行列にする
	# 白成分が多いので白黒を反転させる
	imarray = np.asarray(img.point(lambda x: (255 - x)/255.))
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
		v = encode(io.BytesIO(f.read()))
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

# スペクトラムから特徴量の山を範囲のリストとして抽出する
# * threshold: threshold*[coefficient]を超えないと特徴量として認識しない
def extract_sections(vector, threshold=None):
	secs = []
	sec = [-1, -1]
	for (i, x) in enumerate(vector):
		if x > 0 and sec == [-1, -1]:
			sec[0] = i
		elif x == 0 and sec != [-1, -1]:
			# しきい値(文字幅etc.)より小さいときは保留する
			if not (threshold is None) and (i-sec[0]) < threshold * 0.4:
				continue
			sec[1] = i
			secs.append(sec)
			sec = [-1, -1]
		elif i+1 == len(vector) and sec != [-1, -1]:
			# 画像の末尾に達したときは強制的に特徴量を抽出
			sec[1] = i
			secs.append(sec)
			sec = [-1, -1]
	return secs

# スケーリング
def scale(matrix):
	hsec = extract_sections(map(lambda x: np.mean(x), matrix))
	vsec = extract_sections(map(lambda x: np.mean(x), matrix.T))
	hsec = [hsec[0][0], hsec[-1][1]]
	vsec = [vsec[0][0], vsec[-1][1]]
	output = matrix[hsec[0]:hsec[1]]
	output = output.T[vsec[0]:vsec[1]].T
	return output
 
# 文字をベクトルのリストとして画像から抽出する
def chars(filename):
	im = Image.open(filename).convert("L").resize((400, 400))
	im = np.asarray(im.point(lambda x: 1 - x/255.))
	raw_datas = []

	h = map(lambda x: np.mean(x), im)
	line_secs = extract_sections(h)
	# 行を抽出する
	for (i, sec) in enumerate(line_secs):
		sub = im[sec[0]:sec[1]]
		height = len(sub)
		u = map(lambda x: np.mean(x), sub.T)
		char_secs = extract_sections(u, threshold=height)
		# 文字を抽出する
		for (j, s) in enumerate(char_secs):
			char = sub.T[s[0]:s[1]].T
			char = scale(char)
			char_im = Image.fromarray(char)
			char_im = char_im.resize((400, 400))
			char_im = char_im.point(lambda x: 255*(1-x))
			char_im.save("file/%i_%i.jpg" % (i, j))
			raw_datas.append(char_im)
	
	return raw_datas

# アプリからアップロードされた画像からオフラインOCRを行う
def ocr(filename):
	import romkan
	from sklearn.ensemble import RandomForestClassifier
	#from sklearn.svm import SVC

	fpath = os.path.join(
			os.path.abspath(os.path.dirname(__file__)),
			'file',
			filename)
	# 最新のsvmlightファイルを取得する
	flist = glob.glob('data/feature_*')
	flist.sort(
			cmp=lambda x, y: int(os.path.getctime(x) - os.path.getctime(y)),
			reverse=True)

	datas = chars(fpath)
	result = ""
	for data in datas:
		testX = encode(raw=data)
		trainX, trainY = datasets.load_svmlight_file(flist[0], n_features=1600)
		clf = RandomForestClassifier(n_estimators=413)
		#clf = SVC(C=3.1111111111111112, gamma=1.0)
		clf.fit(trainX.toarray(), trainY)
		result += romkan.to_hiragana(label[int(clf.predict(testX)[0])])

	return result

# tesseract-ocrを用いて文字認識する
# * 英語のみ対応
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
