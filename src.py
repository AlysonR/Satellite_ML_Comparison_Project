import matplotlib.pyplot as plt
import numpy as np

def assign_bin(point):
	global bin_limits
	
	if not np.isnan(point):
		bin_index = next((x[0] for x in enumerate(bin_limits) if x[1] > point), -1)-1
	else:
		return None
	if bin_index >= 0:
		return bin_index
	else:
		return None

def get_X_y(tiles_dir, y_var = 'all_frac', warm_only = False, cloud_only = False, X_vars = ['EIS', 'LTS', 'w500', 'u500', 'v500', 'u850', 'v850', 'u700', 'v700', 'RH900', 'RH850', 'RH700', 'evap', 'sst'], y_min = -1.):
	import glob
	
	files_used = []
	X = []
	y = []
	for filename in glob.glob(tiles_dir + '*.npy'):
		temp = np.load(filename, allow_pickle = True).item()
		if warm_only:
			cool = (temp['warm_frac'] == 0)
			temp['sst'][cool] = np.nan
		if cloud_only:
			clear = (temp['all_fracc'] == 0)
			temp['sst'][clear] = np.nan
		
		for row in range(len(temp['sst'])):
			for tile in range(len(temp['sst'][row])):
				xai = []
				for var in X_vars:
					xai.append(temp[var][row][tile])
				#start with only cloud
				if ((True not in np.isnan(xai)) and (temp[y_var][row][tile] > y_min)):
					X.append(xai)
					y.append(temp[y_var][row][tile])
					if filename not in files_used:
						files_used.append(filename)
					
	return np.array(X), np.array(y), X_vars, files_used

def bin_2d_mean(param1, param2, mean_p):
	global bin_limits
	limits_y = np.percentile(param1, np.linspace(0, 100, 21))
	limits_x = np.percentile(param2, np.linspace(0, 100, 21))
	bins = [[[] for i in range(len(limits_x))] for j in range(len(limits_y))]
	
	bin_limits = limits_y
	y_is = []
	for y in param1:
		y_is.append(assign_bin(y))
	
	bin_limits = limits_x
	x_is = []
	for x in param2:
		x_is.append(assign_bin(x))
	
	for point in range(len(mean_p)):
		if y_is[point] and x_is[point]:
			bins[y_is[point]][x_is[point]].append(mean_p[point])
	
	for i in range(len(bins)):
		for j in range(len(bins[i])):
			if len(bins[i][j]) > 0:
				bins[i][j] = np.nanmean(bins[i][j])
			else:
				bins[i][j] = np.nan
	
	print(bins)
	return bins, limits_y, limits_x
	
def create_swath(filename, predictor, y_var, x_vars, cnc = False, y_min = -1):
	from skimage.metrics import structural_similarity as ssim
	import matplotlib.pyplot as plt
	import copy
	print('creating swath of', filename)
	temp = np.load(filename, allow_pickle = True).item()
	below_ymin =  (np.isnan(temp[y_var]) | (temp[y_var] <= y_min))
	for var in x_vars:
		temp[var][below_ymin] = np.nan
	temp[y_var][below_ymin] = np.nan
	predicted = copy.deepcopy(temp[y_var])
	
	for row in range(len(temp['sst'])):
		for col in range(len(temp['sst'][row])):
			temp_xai = []
			for var in x_vars:
				temp_xai.append(temp[var][row][col])
			if (True not in np.isnan(temp_xai)):
				predicted_y = predictor.predict(np.array([temp_xai]))[0]
				predicted[row][col] = predicted_y
			else:
				predicted[row][col] = np.nan
			
	predicted = np.array(predicted)
	predicted[(np.isnan(predicted))] = 0.
	temp[y_var][(np.isnan(temp[y_var]))] = 0.
	
	mse = np.nanmean(np.square(predicted - temp[y_var]))
	max_all = max([np.nanmax(predicted), np.nanmax(temp[y_var])])
	ss = ssim(temp[y_var], predicted, data_range = max_all)
	
	print(np.amin(predicted), np.amin(temp[y_var]))
	
	plt.subplot(131)
	plt.title('Actual')
	plt.pcolormesh(temp['modis_lons'], temp['modis_lats'], temp[y_var], cmap = 'viridis')
	plt.subplot(132)
	plt.title('Predicted')
	plt.pcolormesh(temp['modis_lons'], temp['modis_lats'], predicted, cmap = 'viridis')
	plt.subplot(133)
	plt.title('Difference')
	plt.pcolormesh(temp['modis_lons'], temp['modis_lats'], temp[y_var] - predicted, cmap = 'inferno')
	plt.colorbar()
	plt.suptitle('{}'.format(ss) + ' SSIM ' + '{}'.format(round(mse, 2)) + ' MSE')
	plt.show()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
