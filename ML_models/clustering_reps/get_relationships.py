import numpy as np
import pickle
import lightgbm as lgbm
from deco import synchronized, concurrent
import glob
import random 

#@concurrent(processes = 12)
def get_relationships(booster, Xs):
	reps = booster.predict(Xs, pred_contrib = True)
	return reps[:, :-1]

#@synchronized
def loop_years(years, lgb):
	for year in years:
		filename = 'cf_{}_globaldaily.pickle'.format(year)
		year_data = pickle.load(open(filename, 'rb'))
		X = year_data[0]
		y = year_data[1]
		X = np.array(X)
		lls = X[:, 1]
		X = X[:, 1:]
		
		all_relationships = [0 for i in range(X.shape[0]//100)]
		for i in range(0, X.shape[0], 100):
			subsample = X[i:i + 100, :]
			all_relationships[int(i/100)] =  get_relationships(lgb.booster_, subsample)
		

		with open('{}_relationships.pickle'.format(year), 'wb') as f:
			pickle.dump([X, y, lls, all_relationships], f)



with open('trained_cf_globaldaily.pickle', 'rb') as f:
	model = pickle.load(f)
loop_years([2004], model)
