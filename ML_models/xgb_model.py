import xgboost as xgb
import numpy as np
import src
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, explained_variance_score, r2_score
import sys
from sklearn.inspection import plot_partial_dependence
import pickle
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
import get_year


y_var = 'cf'
X_variables = ['sst', 'EIS', 'tot_aod','tot_ang', 'w500', 'RH850', 'upper_level_winds']
years = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]


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
	
xgb_model = xgb.XGBRegressor(objective = 'reg:squarederror', booster = 'gbtree', subsample = .25, tree_method = 'hist', learning_rate = .05, eval_metric = 'mse', max_depth = 30, n_estimators = 1000)
xgb_model.fit(train_X, train_y, eval_set = [(eval_X, eval_y), (train_X, train_y)], verbose = 10, eval_metric = 'rmse', early_stopping_rounds = 10)
pred_y = xgb_model.predict(test_X)

mse = mean_squared_error(test_y, pred_y)
exp_var = explained_variance_score(test_y, pred_y)
max_y = np.amax(pred_y)

pickle.dump(xgb_model, open('xgb_train.sav', 'wb'))
print(mse, 'mse', exp_var, 'explained var', max_y, 'maximum y')
evals_results = xgb_model.evals_result()
plt.plot(range(1000), evals_results['validation_0']['rmse'], 'b', label = 'Training')
plt.plot(range(1000), evals_results['validation_1']['rmse'], 'r', label = 'Validation')
plt.legend()
plt.savefig('xgb_training.png')
