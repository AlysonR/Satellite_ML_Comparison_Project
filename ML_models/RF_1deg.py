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

daily = True
y_var = 'cf'
X_vars = ['EIS', 'sst', 'RH700', 'tot_aod','tot_ang', 'upper_level_winds', 'w500']
print('Getting data')

X = []
y = []
years = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013]
print(years[0])
if daily:
	features_dict = get_day.get_single_X_y(X_vars, y_var, years[0])
else:
	features_dict = get_year.get_single_X_y(X_vars, y_var, years[0])

for year in years[1:]:
	print(year)
	if daily:
		temp_dict = get_day.get_single_X_y(X_vars, y_var, year)
	else:
		temp_dict = get_year.get_single_X_y(X_vars, y_var, year)
	for key in features_dict:
		try:
			features_dict[key]['X'].extend(temp_dict[key]['X'])
			features_dict[key]['y'].extend(temp_dict[key]['y'])
		except KeyError:
			#print('not overlapping in region', key)
			try:
				#print(temp_dict[key])
				print(temp_dict[key])
				features_dict[key] = {'X': temp_dict[key]['X'], 'y': temp_dict[key]['y']}
			except KeyError:
				print(key, 'not in temp_dict')
				pass

importances_dict = {}		
for area in features_dict.keys():
	if len(features_dict[area]['X']) < 1200:
		continue
	print(area)
	X = np.array(features_dict[area]['X'])
	y = np.array(features_dict[area]['y'])
	print(X.shape)
	train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)
	reg = RandomForestRegressor()
	reg.fit(train_X, train_y)
	pred_y = reg.predict(test_X)
	mse = mean_squared_error(test_y, pred_y)
	
	r = r2_score(test_y, pred_y)
	print(np.max(pred_y), 'max learned y')
	
	importances_dict[area] = {}
	importances_dict[area]['imps'] = reg.feature_importances_
	importances_dict[area]['mse'] = mse
	importances_dict[area]['r2'] = r
	print(importances_dict[area])
	with open('imp_dic.txt', 'wb') as f:
		pickle.dump(importances_dict, f)
