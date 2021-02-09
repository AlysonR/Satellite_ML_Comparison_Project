import numpy as np
import glob
import sys
import copy
import matplotlib.pyplot as plt
import daily_tools

def get_single_X_y(X_vars, y_var, year):
	months = glob.glob('/gws/nopw/j04/aopp/douglas/*_{}_test.npy'.format(year))
	features_dict = {}
	temp = np.load(months[0], allow_pickle = True).item()
	
	for lat in temp['lats']:
		for lon in temp['lons']:
			features_dict['{}_{}'.format(lat, lon)] = {'X': [], 'y': []}
			
	for month in months:
		print(month)
		month_data = np.load(month, allow_pickle = True).item()
		for day in range(len(month_data['sst'])):
			for n_row in range(len(month_data['sst'][day])):
				for n_tile in range(len(month_data['sst'][day][n_row])):
					lat = month_data['lats'][n_row]
					lon = month_data['lons'][n_tile]
					temp_xai = []
					for feature in X_vars:
						temp_xai.append(month_data[feature][day][n_row][n_tile])
					
					if True not in np.isnan(temp_xai) and True not in np.isnan([month_data[y_var][day][n_row][n_tile]]):
						features_dict['{}_{}'.format(lat, lon)]['X'].append(temp_xai)
						features_dict['{}_{}'.format(lat, lon)]['y'].append(month_data[y_var][day][n_row][n_tile])
	print(np.array(features_dict['0.5_0.5']['X']).shape)
	return features_dict
	
def get_N_X_y(X_vars, y_var, year, N):
	assert (180%N == 0), 'Not divisible grid number'
	
	temp_X_vars = copy.deepcopy(X_vars)
	temp_X_vars.append(y_var)
	months = glob.glob('/gws/nopw/j04/aopp/douglas/*_{}_test.npy'.format(year))
	features_dict = {}
	
	degraded_lons = np.arange(-179.5, 179.5, N)
	degraded_lats = np.arange(90, -90, -1 * N)
	
	for lon in degraded_lons:
		for lat in degraded_lats:
			features_dict['{}_{}'.format(lat, lon)] = {'X': [], 'y': []}
	
	for month in months:
		month_data = np.load(month, allow_pickle = True).item()
		temp_dict = {}
		
		for day in range(len(month_data['sst'])):
			for key in features_dict.keys():
				temp_dict[key] = []
			
			for var in temp_X_vars:
				temp = month_data[var][day].astype(float)
				test = temp.reshape((int(180/N), N, int(360/N), N))
				test = np.rollaxis(test, 1, 3)
				test = test.reshape(int(180/N), int(360/N), N**2)
				
				for i, (lat, t_lat) in enumerate(zip(degraded_lats, test)):
					for lon, t_tile in zip(degraded_lons, test[i]):
						key = '{}_{}'.format(lat, lon)
						temp_dict[key].append(t_tile)
						
			for ll, box in temp_dict.items():
				
				t_xai = []
				for t in range(len(box[0])):
					temp_xai = []
					for n in range(len(temp_X_vars)):
						temp_xai.append(box[n][t])
					if True not in np.isnan(temp_xai):
						t_xai.append(temp_xai)
				
				if len(t_xai) > 0:
					t_xai = np.array(t_xai)
					features_dict[ll]['X'].extend(t_xai[:, :-1])
					features_dict[ll]['y'].extend(t_xai[:, -1])
	
	random_key = list(features_dict.keys())[100]
	print(np.array(features_dict[random_key]['X']).shape)
	print(np.array(features_dict[random_key]['y']).shape)
	temp_X_vars = []
	return features_dict

	
def get_vars_in_N_grid(variables, years, N = 1, remove_nans = False):
	
	degraded_lons = np.arange(-179.5, 179.5, N)
	degraded_lats = np.arange(90, -90, -1 * N)
	
	return_dict = {}
	return_dict['lats'] = degraded_lats
	return_dict['lons'] = degraded_lons
	
	for var in variables:
		return_dict[var] = []
	for year in years:
		print(year)
		for month in glob.glob('/gws/nopw/j04/aopp/douglas/*_{}_test.npy'.format(year)):
			print(month)
			month_data = np.load(month, allow_pickle = True).item()
			for var in variables:
				temp = np.array(month_data[var])
				temp = temp.reshape((temp.shape[0], int(180/N), N, int(360/N), N))
				temp = np.rollaxis(temp, 2, 4)
				temp = temp.reshape((temp.shape[0], int(180/N), int(360/N), N**2))
				temp = np.nanmean(temp, axis = 3)
				if remove_nans:
					bad = np.isnan(temp)
					temp[bad] = 0.
					
				
				return_dict[var].extend(temp)
				
	for var in return_dict.keys():
		return_dict[var] = np.flip(np.array(return_dict[var]), axis = 0)
	return return_dict
	

def get_large_X_y(X_vars, y_var, years, fill_value = -100, nr = 40, nc = 40):
	temp_all = []
	all_vars = X_vars + [y_var]
	features_dict = {}
	
	for year in years:
		print(year)
		for month in glob.glob('/gws/nopw/j04/aopp/douglas/*_{}_test.npy'.format(year)):
			print(month)
			month_data = np.load(month, allow_pickle = True).item()
			#print(month_data.keys())
			#sys.exit()
			collect_xai = []
			
			for var in all_vars:
				temp_xai = []
				temp_var = np.array(month_data[var])
				temp_var = temp_var[:, 30:-30, :]
				for day in range(temp_var.shape[0]):
					blocked = blockshaped(temp_var[day], nr, nc)
					temp_xai.extend(blocked)
					
				temp_xai = np.array(temp_xai)
				collect_xai.append(temp_xai)
			collect_xai = np.array(collect_xai)
			collect_xai = np.rollaxis(collect_xai, 0, 4)
			non_nan = []
			for tile in range(collect_xai.shape[0]):
				nan_count = np.count_nonzero(np.isnan(collect_xai[tile]))
				
				if nan_count/(nr * nc) < .1:
					non_nan.extend(collect_xai[tile])
			
			bad = np.full(collect_xai.shape, False)
			for dimension in range(collect_xai.shape[-1]):
				bad_var = np.isnan(collect_xai[:, :, :, dimension])
				bad[bad_var] = True
			collect_xai[bad] = fill_value
			
			temp_all.extend(collect_xai)
	temp_all = np.array(temp_all)
	
	features_dict['X'] =  temp_all[:, :, :, :-1]
	features_dict['y'] = temp_all[:, :, :, -1]
	print(features_dict['X'].shape)
	
	
	return features_dict	
#from stackoverflow im not above "help"
def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
    
    assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))

#get_large_X_y(['EIS', 'sst'], 'cf', range(2003, 2004))
#get_N_X_y(['EIS', 'sst', 'tot_ang', 'tot_aod'], 'cf', 2008, 4)
#get_quad_X_y(['EIS', 'sst', 'tot_ang', 'tot_aod'], 'cf', 2007)
#get_single_X_y(['EIS', 'sst', 'tot_ang', 'tot_aod'], 'cf', 2007)

