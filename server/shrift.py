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

SIZE = 400	# 文字画像の縦横サイズ
SPLIT = 20	# 認識対象の縦横分割数
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
	'wa', 'wo', 'n',
	'ga', 'gi', 'gu', 'ge', 'go',
	'za', 'zi', 'zu', 'ze', 'zo',
	'da', 'di', 'du', 'de', 'do',
	'ba', 'bi', 'bu', 'be', 'bo',
	'pa', 'pi', 'pu', 'pe', 'po',
]

# 小文字
small_label = [
	'a', 'i', 'u', 'e', 'o',
	'tu', 'ya', 'yu', 'yo',
]

clf = None

# 学習器の生成
def generate_classifier():
	sys.stdout.write(" * Generating Classifier ... ")
	from sklearn.ensemble import RandomForestClassifier
	global clf
	# 最新のsvmlightファイルを取得する
	flist = glob.glob('data/feature_*')
	flist.sort(
			cmp=lambda x, y: int(os.path.getctime(x) - os.path.getctime(y)),
			reverse=True)

	try:
		trainX, trainY = datasets.load_svmlight_file(flist[0], n_features=SPLIT**2)
		clf = RandomForestClassifier(n_estimators=508)
		clf.fit(trainX.toarray(), trainY)
		print("generated!")
	except ValueError as e:
		print("cannot generate (%s)" % e)

# 手書き文字1文字から特徴ベクトルを生成する
# Algorithm:
#	ShriftTrainerはSIZE*SIZEの画像を返すので、グレースケール化して
#	小区画の平均をとり、SPLIT**2次元の特徴ベクトルとする
# Vector: SPLIT*SPLITのSPLIT**2次元濃淡ベクトル
# Class: 各文字と一対一対応した整数値
def encode(raw_str="", raw=None):
	img = raw
	if img is None:
		img = Image.open(raw_str).convert('L')

	img = img.resize((SIZE, SIZE))

	# グレースケール化した画像を行列にする
	# 白成分が多いので白黒を反転させる
	imarray = np.asarray(img.point(lambda x: (255 - x)/255.))
	# 小区画の一辺のピクセル数
	s = SIZE/SPLIT
	return np.array([
		[imarray[s*i:s*(i+1),s*j:s*(j+1)].mean()
			for i in range(0, SPLIT)
			for j in range(0, SPLIT)
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
# * threshold 
def extract_sections(vector, threshold=None):
	secs = []
	sec = [-1, -1]
	for (i, x) in enumerate(vector):
		if x > 0 and sec == [-1, -1]:
			# 特徴量の検出
			sec[0] = i
		elif x == 0 and sec != [-1, -1]:
			# 特徴量の検出終了
			sec[1] = i
			secs.append(sec)
			sec = [-1, -1]
		elif i+1 == len(vector) and sec != [-1, -1]:
			# 画像の末尾に達したときは強制的に特徴量を抽出
			sec[1] = i
			secs.append(sec)
			sec = [-1, -1]
	
	result = []
	# しきい値(threshold)を元に文字抽出リストを修正する
	if not (threshold is None):
		# x < ts*0.15			-> 0
		# ts*0.15 < x < ts*0.6	-> 1
		# ts*0.6 < x			-> 2
		ts = [
				2 if (s[1]-s[0]) > threshold*0.6
				else
					0 if (s[1]-s[0]) < threshold*0.15 else 1
				for s in secs]
		print ts
		skip = False
		for (i, too_small) in enumerate(ts):
			if skip:
				skip = False
				continue
			if i+1 == len(ts):
				result.append(secs[i])
			elif too_small == 2 and ts[i+1] == 2:
				result.append(secs[i])
			elif too_small == 2 and ts[i+1] == 0 \
				or too_small == 1 \
				or too_small == 0:
				result.append([secs[i][0], secs[i+1][1]])
				skip = True
			else:
				result.append(secs[i])
	else:
		result = secs

	return result

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
	im = Image.open(filename).convert("L").resize((SIZE, SIZE))
	im = np.asarray(im.point(lambda x: 1 - x/255.))
	raw_datas = []	# 各文字の生データ
	small = []		# 小文字かどうか

	h = map(lambda x: np.mean(x), im)
	line_secs = extract_sections(h)
	# 行を抽出する
	for (i, sec) in enumerate(line_secs):
		sub = im[sec[0]:sec[1]]
		height = len(sub)
		u = map(lambda x: np.mean(x), sub.T)
		char_secs = extract_sections(u, threshold=height)
		print char_secs,height
		# 文字を抽出する
		for (j, s) in enumerate(char_secs):
			char = sub.T[s[0]:s[1]].T
			v = extract_sections(map(lambda x: np.mean(x), char))
			# 行の高さと文字の高さを比較して小文字判定する
			if len(v) == 1 and (v[0][1]-v[0][0]) < height*0.6:
				small.append(True)
			else:
				small.append(False)
			char = scale(char)
			char_im = Image.fromarray(char)
			char_im = char_im.resize((SIZE, SIZE))
			char_im = char_im.point(lambda x: 255*(1-x))
			char_im.save("file/%i_%i.jpg" % (i, j))
			raw_datas.append(char_im)
	
	return raw_datas, small

# アプリからアップロードされた画像からオフラインOCRを行う
def ocr(filename):
	import romkan
	fpath = os.path.join(
			os.path.abspath(os.path.dirname(__file__)),
			'file',
			filename)
	datas, small = chars(fpath)
	result = ""
	for (i, data) in enumerate(datas):
		testX = encode(raw=data)
		rom = label[int(clf.predict(testX)[0])]
		proba = clf.predict_proba(testX)[0]
		print max(proba)
		#import matplotlib.pyplot as plt
		#plt.plot(proba)
		#plt.show()
		# 小文字判定
		if small[i] and rom in small_label:
			rom = 'x' + rom

		c = romkan.to_hiragana(rom)
		sys.stdout.write(c)
		result += c
	sys.stdout.write('\n')

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

generate_classifier()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise RuntimeError('too few args')
	srcname = sys.argv[1]
	print ocr(srcname)
