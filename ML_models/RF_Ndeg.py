import numpy as np
import src
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, explained_variance_score, r2_score
import sys
from sklearn.inspection import plot_partial_dependence
import pickle
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
import get_year
sys.path.append('/home/users/rosealyd/ML_sat_obs/daily/')
import get_day

N = 2
y_var = 'cf'
X_vars = ['sst', 'EIS', 'RH700', 'tot_aod','tot_ang', 'upper_level_winds', 'w500', 'CAPE']
print('Getting data')

X = []
y = []
years = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]
print(years[0])
features_dict = get_day.get_N_X_y(X_vars, y_var, years[0], N = N)
for year in years[1:]:
	print(year)
	temp_dict = get_day.get_N_X_y(X_vars, y_var, year, N = N)
	for key in features_dict:
		
		features_dict[key]['X'].extend(temp_dict[key]['X'])
		features_dict[key]['y'].extend(temp_dict[key]['y'])

importances_dict = {}		
for area in features_dict.keys():
	if len(features_dict[area]['X']) < 6000:
		continue
	print(area)
	X = np.array(features_dict[area]['X'])
	y = np.array(features_dict[area]['y'])
	print(X.shape)
	train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)
	reg = RandomForestRegressor(n_estimators = 125, min_samples_leaf = 5, max_depth = 25, min_samples_split = 10, bootstrap = True)
	reg.fit(train_X, train_y)
	pred_y = reg.predict(test_X)
	t_pred_y = reg.predict(train_X)
	mse = mean_squared_error(test_y, pred_y)
	t_mse = mean_squared_error(train_y, t_pred_y)
	
	r = r2_score(test_y, pred_y)
	print(np.max(pred_y), 'max learned y')
	
	importances_dict[area] = {}
	importances_dict[area]['imps'] = reg.feature_importances_
	importances_dict[area]['mse'] = mse
	importances_dict[area]['r2'] = r
	importances_dict[area]['train_mse'] = t_mse
	print(importances_dict[area])
	with open('imp_dic_{}.txt'.format(N), 'wb') as f:
		pickle.dump(importances_dict, f)
