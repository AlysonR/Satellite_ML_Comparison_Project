import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFE
from sklearn.inspection import partial_dependence
from sklearn.metrics import mean_squared_error
import sklearn
import src
from sklearn import tree
import sys
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
import get_year
from sklearn.tree import export_graphviz
from sklearn.metrics import confusion_matrix
import copy
import glob
import graphviz

quick_plot = False
warm = True



print('The scikit-learn version is {}.'.format(sklearn.__version__))

tiles_dir = '/home/users/rosealyd/ML_sat_obs/cloudy_tiles/'
y_var = 'cf'
X_vars = ['LTS', 'sst', 'w500', 'RH850', 'tot_ai']
X = []
y = []
for year in [2007, 2008, 2009, 2010]:
	print(year)
	tX, ty, X_vars, files  = get_year.get_as_X_y(X_vars, y_var, 2007)
	X.extend(tX)
	y.extend(ty)
X = np.array(X)
y = np.array(y)
#X_vars = ['dust', 'hbc', 'pbc', 'dms', 'oc', 'su', 'ss', 'msa']
#X, y, X_vars, files = src.get_X_y(tiles_dir, X_vars = X_vars, warm_only = warm, y_var = y_var)
print(len(files), 'number of files')
nan_y = np.isnan(y)
print(y[nan_y], 'nan y test')
print(len(y), 'number samples')

train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)

regression = RandomForestRegressor(max_depth = 30, max_features = 5, random_state = 30, n_jobs = 10,  n_estimators = 100, min_samples_split = 5)
regression.fit(train_X, train_y)

print([round(p, 2) for p in regression.feature_importances_.tolist()])

print(regression.score(test_X, test_y), 'score')
pred_y = regression.predict(test_X)
print(mean_squared_error(test_y, pred_y), 'overall mse')

get_year.plot_year(regression, X_vars, y_var, 2010)
#for filename in files:
#	src.create_swath(filename, regression, y_var, X_vars, y_min = 0)


