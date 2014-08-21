#!/usr/bin/env python
# coding: utf-8

import sys
import numpy as np
from sklearn import datasets, grid_search
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

SIZE = 10.

algorithm = {
		'svm': SVC(),
		'rf': RandomForestClassifier()
}

parameters = {
		'svm': {
			'C': np.linspace(1, 20, SIZE),
			'gamma': np.linspace(1, 2000, SIZE)
		},
		'rf': {
			'n_estimators': np.arange(583, 590)
		}
}

if __name__ == '__main__':
	if len(sys.argv) < 3:
		raise RuntimeError('too few args')
	elif not (sys.argv[1] in algorithm):
		raise RuntimeError('no algorithm `%s`' % sys.argv[1])
	
	trainX, trainY = datasets.load_svmlight_file(sys.argv[2], n_features=1600)
	clf = grid_search.GridSearchCV(
			algorithm[sys.argv[1]],
			parameters[sys.argv[1]],
			scoring='accuracy',
			n_jobs=-1)

	if sys.argv[1] == 'rf':
		trainX = trainX.toarray()

	clf.fit(trainX, trainY)
	
	predY = clf.predict(trainX)
	best = clf.best_estimator_
	print "BestEstimator: %s\nAccuracy=%s%%" \
			% (best, accuracy_score(trainY, predY))
