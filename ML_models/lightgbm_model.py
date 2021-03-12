import numpy as np
import src
import matplotlib.pyplot as plt
import lightgbm as lgbm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, explained_variance_score, r2_score
import sys
from sklearn.inspection import plot_partial_dependence
import pickle
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
import get_year

y_var = 'cf'
X_variables = ['sst', 'EIS', 'tot_aod','tot_ang', 'w500', 'RH850', 'upper_level_winds', 'evap', 'u850']
years = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]
objective = 'mse'
run = True

if run:
	print('Running and training lightgbm with', objective, 'and', y_var)
	print('Getting data')

	X = []
	y = []
	
	for year in years:
		print(year)
		tX, ty  = get_year.get_as_X_y(X_variables, y_var, year)
		if year == years[0]:
			X = tX
			y = ty
		else:
			X = np.hstack((X, tX))
			y = np.hstack((y, ty))
		print(X.shape)
		print(y.shape)
	X = X.T
	
	train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)
	eval_X, train_X, eval_y, train_y = train_test_split(train_X, train_y, test_size = .2, random_state = 37)
	
	bst_1 = lgbm.LGBMRegressor(n_estimators = 1000, learning_rate = .015, objective = objective, boosting = 'goss')

	bst_1.fit(train_X, train_y, eval_set = [(eval_X, eval_y), (train_X, train_y)], early_stopping_rounds = 7, verbose = 10)

	#plot_partial_dependence(bst_1, train_X, ['tot_aod', ('RH850', 'tot_aod')], feature_names = X_variables, n_jobs = 3, grid_resolution = 5)
	#plt.show()
	pred_y = bst_1.predict(test_X)
	print(mean_squared_error(test_y, pred_y), 'mse')
	print(explained_variance_score(test_y, pred_y), 'explained variance')
	print(np.max(pred_y), 'max learned y')
	#lgbm.plot_metric(bst_1)
	#plt.show()

	pickle.dump(bst_1, open('lightgbm_GCMcomp_{}_{}.sav'.format(y_var, objective), 'wb'))
else:
	print('Loading pre-trained model' + 'lightgbm_test_re_{}.sav'.format(objective))
	#bst_1 = pickle.load(open('lightgbm_GCMcomp_{}_{}.sav'.format(y_var, objective)))
	
similarities = []
differences = []
for year in years:
	print(year)
	sims, diffs = get_year.plot_year(bst_1, X_variables, y_var, year, GCM = True)
	similarities.extend(sims)
	differences.append(diffs)
#np.save('{}_sims_diffs_lgbm'.format(objective), [similarities, differences])
plt.scatter(sims, diffs)
plt.show()
#plt.hist(similarities)
#plt.show()
