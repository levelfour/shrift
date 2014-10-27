#!/usr/bin/env python
# coding: utf-8

from config import *
import os, sys, re, datetime
import io
import glob
from PIL import Image
import numpy as np
from sklearn import datasets

# TODO: paramter
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
		# TODO: paramter
		clf = RandomForestClassifier(n_estimators=585)
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

# スペクトルから特徴量の山を範囲のリストとして行を抽出する
def extract_lines(vector):
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

	heights = np.array(map(lambda s: s[1]-s[0], secs))
	# 「う」のような文字の行スペクトルを見ると2文字に
	# 分離してしまうので、行高の小さい行に対して補正をかける
	while heights.max() > heights.min() * 3: # TODO: parameter
		min_i = np.argmin(heights)
		if min_i < len(secs) - 1:
			# 「う」「え」「ら」等の抽出に対応
			heights[min_i] += heights[min_i+1]
			secs[min_i] = [secs[min_i][0], secs[min_i+1][1]]
			heights = np.delete(heights, min_i+1)
			secs = np.delete(secs, min_i+1, axis=0)
		else:
			# 「き」「こ」「さ」等の抽出に対応
			heights[min_i] += heights[min_i-1]
			secs[min_i] = [secs[min_i-1][0], secs[min_i][1]]
			heights = np.delete(heights, min_i-1)
			secs = np.delete(secs, min_i-1, axis=0)
	
	return secs

# スペクトルから特徴量の山を範囲のリストとして文字を抽出する
# * threshold 
def extract_characters(vector, threshold=None):
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
		result.append([])
		# TODO: parameter
		# x < ts*0.15			-> 0(濁点、半濁点など)
		# ts*0.15 < x < ts*0.6	-> 1(「い」「け」等の縦棒)
		# ts*0.6 < x			-> 2(通常の文字)
		ts = [
				2 if (s[1]-s[0]) > threshold*0.6
				else
					0 if (s[1]-s[0]) < threshold*0.15 else 1
				for s in secs]
		print ts
		# 行データから尤もらしい文字の抽出の仕方を返す再帰関数
		def gen_data(i):
			if i == len(ts):
				return [[]]
			elif i+1 == len(ts):
				return [[secs[i]]]
			elif i <= len(ts) - 3 and ts[i] != 2 \
					and ts[i+1] != 2 and ts[i+2] != 2:
				# 「ふ」判定用
				a = gen_data(i+3)
				[v.insert(0, [secs[i][0],secs[i+2][1]])
					for v in a]
				b = gen_data(i+2)
				[v.insert(0, [secs[i][0],secs[i+1][1]])
					for v in b]
				return a+b
			elif ts[i] == 2 and ts[i+1] != 2 or ts[i] == 1 or ts[i] == 0:
				a = gen_data(i+2)
				[v.insert(0, [secs[i][0],secs[i+1][1]])
					for v in a]
				b = gen_data(i+1)
				[v.insert(0, secs[i]) for v in b]
				return a+b
			else:
				a = gen_data(i+1)
				[v.insert(0, secs[i]) for v in a]
				return a
		
		result = gen_data(0)
	else:
		result = secs

	return result

# スケーリング
def scale(matrix):
	hsec = extract_lines(map(lambda x: np.mean(x), matrix))
	vsec = extract_characters(map(lambda x: np.mean(x), matrix.T))
	hsec = [hsec[0][0], hsec[-1][1]]
	vsec = [vsec[0][0], vsec[-1][1]]
	output = matrix[hsec[0]:hsec[1]]
	output = output.T[vsec[0]:vsec[1]].T
	return output
 
# 文字をベクトルのリストとして画像から抽出する
# @return: ([文字の生データ], [小文字])の想定されうるパターンのリスト
#	-> 行ごとのリストになっている
def chars(filename):
	im = Image.open(filename).convert("L").resize((SIZE, SIZE))
	im = np.asarray(im.point(lambda x: 1 - x/255.))
	datas = []	# 各文字の生データ

	h = map(lambda x: np.mean(x), im)
	line_secs = extract_lines(h)
	# 行を抽出する
	for (i, sec) in enumerate(line_secs):
		line_datas = []
		sub = im[sec[0]:sec[1]]
		height = len(sub)
		u = map(lambda x: np.mean(x), sub.T)
		char_secs_list = extract_characters(u, threshold=height)
		# 文字を抽出する
		for char_secs in char_secs_list:
			raw_data = []
			small = []	# 小文字かどうか
			for (j, s) in enumerate(char_secs):
				char = sub.T[s[0]:s[1]].T
				v = extract_characters(map(lambda x: np.mean(x), char))
				# 行の高さと文字の高さを比較して小文字判定する
				# TODO: parameter
				if len(v) == 1 and (v[0][1]-v[0][0]) < height*0.6:
					small.append(True)
				else:
					small.append(False)
				char = scale(char)
				char_im = Image.fromarray(char)
				char_im = char_im.resize((SIZE, SIZE))
				char_im = char_im.point(lambda x: 255*(1-x))
				raw_data.append(char_im)
			line_datas.append((raw_data, small))
		datas.append(line_datas)
	
	return datas

# アプリからアップロードされた画像からオフラインOCRを行う
def ocr(filename):
	import romkan
	fpath = os.path.join(
			os.path.abspath(os.path.dirname(__file__)),
			'file',
			filename)
	datalist = chars(fpath)
	ocr_str = ""
	for (line_n, line_datas) in enumerate(datalist):
		result = []
		likelihoods = []
		for datas in line_datas:
			datas, small = datas
			s = ""	# 認識結果文字列
			l = 1	# 認識結果のscore(=尤度の総和**(1/文字列長))
			for (i, data) in enumerate(datas):
				testX = encode(raw=data)
				rom = label[int(clf.predict(testX)[0])]
				proba = clf.predict_proba(testX)[0]
				l *= max(proba) # 尤度をかける
				# 小文字判定
				if small[i] and rom in small_label:
					rom = 'x' + rom

				s += romkan.to_hiragana(rom)
			# パターンごとの文字列長の違いを吸収する
			l = l**(1./len(datas))
			print("%s (%f)" % (s, l))
			result.append(s)
			likelihoods.append(l)
	
		# 認識結果のscoreが最大のものを採用する
		like_i = np.argmax(likelihoods)
		ocr_str += (result[like_i] + '\n')

		# 選択した抽出結果を画像として出力する
		for img in datalist[line_n][like_i][0]:
			img.save('file/{}_{}.jpg'.format(
				line_n, datalist[line_n][like_i][0].index(img)))

	ocr_str = ocr_str.rstrip()
	print u"Result: {}".format(ocr_str)
	return ocr_str

generate_classifier()

if __name__ == "__main__":
	if len(sys.argv) < 2:
		raise RuntimeError('too few args')
	srcname = sys.argv[1]
	print ocr(srcname)
