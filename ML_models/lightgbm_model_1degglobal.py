import numpy as np
import src
import matplotlib.pyplot as plt
import lightgbm as lgbm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, explained_variance_score, r2_score
import sys
from sklearn.inspection import plot_partial_dependence
import pickle
sys.path.append('/home/users/rosealyd/ML_sat_obs/daily/')
import get_day

y_var = 'cf'
X_vars = ['sst', 'EIS', 'tot_aod','tot_ang', 'w500','RH700','RH850', 'upper_level_winds', 'evap', 'u850', 'CAPE', 'v850']
years = range(2004, 2020)
load = True
Xs = []
ys = []
for year in years:
	print('getting', year)
	if not load:
		temp_X, temp_y = get_day.get_global_X_y(X_vars, y_var, year, get_lat_lon = True)
		Xs.extend(temp_X)
		ys.extend(temp_y)
		print('saving pickle')
		with open('{}_{}_globaldaily.pickle'.format(y_var,year), 'wb') as f:
			pickle.dump([temp_X, temp_y], f)
	else:
		print('loading pickle')
		with open('./clustering_reps/{}_{}_globaldaily.pickle'.format(y_var, year), 'rb') as f:
			temp = pickle.load(f)
		Xs.extend(temp[0])
		ys.extend(temp[1])
Xs = np.array(Xs)
lls = Xs[:, 0]
Xs = np.array(Xs[:, 1:])
ys = np.array(ys)

		
print(Xs.shape)	
train_X, test_X, train_y, test_y = train_test_split(Xs, ys, test_size = .4)
eval_X, test_X, eval_y, test_y = train_test_split(test_X, test_y, test_size = .5)
print('Training')
bst_1 = lgbm.LGBMRegressor(n_estimators = 100, learning_rate = .1, subsample = .9, objective = 'mse', boosting = 'goss', max_depth = 50, num_leaves = 500)
bst_1.fit(train_X, train_y, eval_set = [(eval_X, eval_y), (train_X, train_y)], early_stopping_rounds = 30, verbose = 10)

with open('trained_{}_globaldaily.pickle'.format(y_var), 'wb') as f:
	pickle.dump(bst_1, f)
