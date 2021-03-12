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
import get_trendline
import time

start_time = int(time.time())


N = 1
y_var = 'cf'
X_vars = ['sst', 'EIS', 'RH700', 'tot_aod','tot_ang', 'RH900', 'w500', 'evap', 'upper_level_winds', 'u850', 'v850']
cloud_vars = ['l_re', 'cod', 'cth', 'cwp']
X_vars.extend(cloud_vars)
print('Getting data')

X = []
y = []
years = range(2003, 2020)

print(years[0])
features_dict = get_day.get_single_X_y(X_vars, y_var, years[0])
for year in years[1:]:
	print(year)
	temp_dict = get_day.get_single_X_y(X_vars, y_var, year)
	for key in features_dict:
		
		features_dict[key]['X'].extend(temp_dict[key]['X'])
		features_dict[key]['y'].extend(temp_dict[key]['y'])

importances_dict = {}	
importances_dict['features'] = X_vars
importances_dict['cloud_features'] = cloud_vars
importances_dict['target'] = y_var
	
for area in features_dict.keys():
	if len(features_dict[area]['X']) < 5000:
		continue
	print(area)
	with open('/gws/nopw/j04/aopp/douglas/1deg_tiles/{}.txt'.format(area), 'wb') as f:
		pickle.dump(features_dict, f)
	
	'''	
	y = np.array(features_dict[area]['y'])
	cloudy = (y > 0)
	X = np.array(features_dict[area]['X'])
	y = y[cloudy]
	X = X[cloudy]
	
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
	importances_dict[area]['trendlines'] = {}
	print(X.shape)
	for var in range(len(X_vars)):
		try:
			importances_dict[area]['trendlines'][X_vars[var]] = get_trendline.get_trendline_slope(reg, X, y, var)
		except:
			importances_dict[area]['trendlines'][X_vars[var]] = np.nan
	print(importances_dict[area])
	with open('RF_imp_dic_{}_{}.txt'.format(start_time, N), 'wb') as f:
		pickle.dump(importances_dict, f)
	'''
