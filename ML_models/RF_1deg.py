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
years = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010]
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
	train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .1, random_state = 37)
	reg = RandomForestRegressor()
	pred_y = reg.predict(test_X)
	print(mean_squared_error(test_y, pred_y), 'mse')
	print(r2_score(test_y, pred_y), 'r2')
	print(np.max(pred_y), 'max learned y')
	#lgbm.plot_importance(bst_1)
	#plt.show()
	importances_dict[area] = reg_1.feature_importances_
	print(importances_dict[area])
	sys.exit()
