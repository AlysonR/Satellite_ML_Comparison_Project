import numpy as np
import src
import matplotlib.pyplot as plt
import lightgbm as lgbm
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, explained_variance_score, r2_score
import sys
import pickle
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
import get_year

tiles_dir = '/home/users/rosealyd/ML_sat_obs/cloudy_tiles/'

y_var = 'cf'
X_vars = ['LTS', 'sst', 'RH700', 'modis_aod', 'upper_level_U', 'upper_level_V', 'w500']
print('Getting data')

#X, y, X_vars, files = src.get_X_y(tiles_dir, X_vars = X_vars, y_var = y_var, y_min = -1)
X = []
y = []
for year in [2004, 2005, 2006, 2007, 2008, 2009, 2010]:
	print(year)
	tX, ty, X_vars, files  = get_year.get_as_X_y(X_vars, y_var, 2007)
	X.extend(tX)
	y.extend(ty)
X = np.array(X)
y = np.array(y)
print(X.shape)

train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)
eval_X, train_X, eval_y, train_y = train_test_split(train_X, train_y, test_size = .2, random_state = 37)

bst_1 = lgbm.LGBMRegressor(n_estimators = 1500, boosting = 'dart', learning_rate = .02, objective = 'rmse')

bst_1.fit(train_X, train_y, eval_set = [(eval_X, eval_y), (train_X, train_y)], early_stopping_rounds = 10, verbose = 10)



pickle.dump(bst_1, open('lightgbm_latest.sav', 'wb'))

pred_y = bst_1.predict(test_X)
print(mean_squared_error(test_y, pred_y), 'mse')
print(explained_variance_score(test_y, pred_y), 'explained variance')
print(r2_score(test_y, pred_y), 'r2')
print(np.max(pred_y))
lgbm.plot_metric(bst_1)
plt.show()
lgbm.plot_importance(bst_1)
plt.show()
get_year.plot_year(bst_1, X_vars, y_var, 2007)
