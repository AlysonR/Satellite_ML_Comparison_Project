import numpy as np
import src
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import sys

tiles_dir = '/home/users/rosealyd/ML_sat_obs/cloudy_tiles/'

y_var = 're'
X_vars = ['LTS', 'sst', 'w500', 'RH850', 'tot_ai']
print('Getting data')
X, y, X_vars, files = src.get_X_y(tiles_dir, X_vars = X_vars, y_var = y_var, y_min = 0.)
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)


#loss function reg:linear for regression
bst = xgb.XGBRegressor(objective = 'reg:squarederror', booster = 'gbtree', subsample = .25, tree_method = 'hist', learning_rate = .05, eval_metric = 'mae', max_depth = 30, n_estimators = 100)
print('Fitting')
bst.fit(train_X, train_y)
preds = bst.predict(test_X)
print(np.nanmean(test_y), np.nanmean(preds))

mse = mean_squared_error(test_y, preds)

print(mse, 'mean square error')

for filename in files:
	src.create_swath(filename, bst, y_var, X_vars)
