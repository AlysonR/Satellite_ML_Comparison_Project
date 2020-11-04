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
from sklearn.tree import export_graphviz
from sklearn.metrics import confusion_matrix
import copy
import glob
from skimage.metrics import structural_similarity as ssim

quick_plot = True
warm = True

print('The scikit-learn version is {}.'.format(sklearn.__version__))

tiles_dir = '/home/users/rosealyd/ML_sat_obs/sc_test_cloudy_tiles/'
y_var = 'sc_frac'
X_vars = ['LTS', 'sst', 'w500', 'RH850', 'evap']
#X_vars = ['dust', 'hbc', 'pbc', 'dms', 'oc', 'su', 'ss', 'msa']
X, y, X_vars, files = src.get_X_y(tiles_dir, X_vars = X_vars, warm_only = warm, y_var = y_var)
print(len(X), 'number of X')

train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)

regression = RandomForestRegressor(max_depth = 30, max_features = 5, random_state = 30, n_jobs = 10,  n_estimators = 100, min_samples_split = 5)
regression.fit(train_X, train_y)

print([round(p, 2) for p in regression.feature_importances_.tolist()])

print(regression.score(test_X, test_y))
pred_y = regression.predict(test_X)
print(mean_squared_error(test_y, pred_y), 'overall mse')

mses = []
ssims = []

print(len(files), 'number modis swaths')

for tile_fn in files:
	temp = np.load(tile_fn, allow_pickle = True).item()
	
	predicted_cf = [[0 for i in temp[y_var][0]] for j in temp[y_var]]
	clear = (temp[y_var] == 0)
	bad = (np.isnan(temp[y_var]))
	temp[y_var][bad] = 0.
	if warm:
		cool = (temp['warm_frac'] == 0)
		temp[y_var][cool] = 0.
	temp[y_var][clear] = 0.
	
	for row in range(len(temp['sst'])):
		for tile in range(len(temp['sst'][row])):
			temp_xai = []
			for var in X_vars:
				temp_xai.append(temp[var][row][tile])
			if (True not in np.isnan(temp_xai)) and (temp[y_var][row][tile] > 0):
				predicted_cf[row][tile] = regression.predict([temp_xai])[0]
			else:
				predicted_cf[row][tile] = 0.	
	
	predicted_cf = np.array(predicted_cf)
	mses.append(np.square(predicted_cf - temp[y_var]).mean(axis = None))
	max_all = max([np.amax(predicted_cf), np.amax(temp[y_var])])
	ssims.append(ssim(temp[y_var], predicted_cf, data_range = max_all))
	print(ssims[-1])
	plt.subplot(131)
	plt.title('Actual observed')
	plt.pcolormesh(temp['modis_lons'], temp['modis_lats'], temp[y_var], cmap = 'inferno')
	plt.subplot(132)
	plt.title('ML predicted')
	plt.pcolormesh(temp['modis_lons'], temp['modis_lats'], predicted_cf, cmap = 'inferno')
	#plt.colorbar()
	plt.suptitle('{} SSIM out of 1, {} MSE'.format(round(ssims[-1], 2), round(mses[-1], 3)))
	plt.subplot(133)
	plt.title('Differenced')
	plt.pcolormesh(temp['modis_lons'], temp['modis_lats'], temp[y_var] - predicted_cf, cmap = 'viridis')
	plt.colorbar()
	plt.show()
plt.scatter(mses, ssims)
plt.xlabel('MSE')
plt.ylabel('SSIM')
plt.savefig('mse_ssim.png')
plt.show()




