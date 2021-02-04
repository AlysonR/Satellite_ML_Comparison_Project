import numpy as np
import sys
sys.path.append('/home/users/rosealyd/ML_sat_obs/GCM_comp/')
import hadgem_comp
import matplotlib.pyplot as plt
import cmap
import copy
from skimage.metrics import structural_similarity as ssim

year_dir = '/home/users/rosealyd/ML_sat_obs/monthly/'


def get_as_X_y(X_vars, y_var, year):
	global year_dir
	year_data = np.load(year_dir + str(year)+ '.npy', allow_pickle = True).item()
	
	xais = []
	yais = []
	temp_vars = copy.deepcopy(X_vars)
	temp_vars.append(y_var)
	for month in range(len(year_data['sst'])):
		temp = []
		for var in temp_vars:
			test = year_data[var][month].ravel()
			temp.append(test)
		temp = np.array(temp)
		if month == 0:
			xais = temp
		else:
			xais = np.hstack((xais, temp))
		
		
	
	xais = np.array(xais)
	print(np.nanmin(xais, axis = 1))
	print(np.nanmax(xais, axis = 1))
	xais = xais[:, ~np.isnan(xais).any(axis = 0)]
	
	
	ys = xais[-1, :]
	xais = xais[:-1, :]
	return xais, ys


def plot_year(predictor, X_vars, y_var, year, GCM = False):
	global year_dir
	import datetime
	if GCM:
		year_data = hadgem_comp.get_hadgem()
		y_var = 'cf'
		year = 1850
	else:
		year_data = np.load(year_dir + str(year) + '.npy', allow_pickle = True).item()
	pred_y = np.zeros(year_data[y_var][0].shape)
	ssims = []
	mean_diffs = []
	for month in range(len(year_data['sst']))[10:]:
		date = datetime.date(month = month + 1, year = year, day = 1)
		print(date.strftime('%B'), 'date')
		
		for lat_row in range(len(year_data['sst'][month])):
			for lon_tile in range(len(year_data['sst'][month][lat_row])):
				xai = []
				for var in X_vars:
					xai.append(year_data[var][month][lat_row][lon_tile])
				if True in np.isnan(xai):
					pred_y[lat_row][lon_tile] = np.nan
				else:
					pred_y[lat_row][lon_tile] = predictor.predict([xai])[0]
				print(xai)
		land = np.isnan(pred_y)
		year_data[y_var][month][land] = np.nan
		over = (pred_y > np.max(year_data[y_var][month]))
		pred_y[over] = np.max(year_data[y_var][month])
		print(np.nanmean(pred_y), 'predicted mean')
		print(np.nanmean(year_data[y_var][month]), 'actual mean')
		mean_diffs.append(np.nanmean(pred_y) - np.nanmean(year_data['cf'][month]))
		
		plot_max = max([np.nanmax(pred_y), np.nanmax(year_data[y_var][month])])
		plot_min = min([np.nanmin(pred_y), np.nanmin(year_data[y_var][month])])
		
		plt.pcolormesh(pred_y)
		plt.colorbar()
		plt.show()
		
		plt.subplot(121)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], pred_y, cmap = 'cividis', vmin = plot_min, vmax = plot_max)
		plt.title('Predicted CF')
		plt.colorbar()
		plt.subplot(122)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], pred_y - year_data[y_var][month], cmap = cmap.get_cmap())
		plt.title('Differenced CF')
		plt.colorbar()
		plt.suptitle('{} {}'.format(date.strftime('%B'), date.strftime('%Y')))
		plt.savefig('GCM Test')
		plt.show()
		pred_y[np.isnan(pred_y)] = 0.
		year_data[y_var][month][np.isnan(year_data[y_var][month])] = 0.
		sys.exit()
		similarity = ssim(pred_y, year_data[y_var][month], data_range = max([np.amax(pred_y), np.amax(year_data[y_var][month])]))
		print(similarity)
		ssims.append(similarity)
	return ssims, mean_diffs

def get_single_X_y(X_vars, y_var, year):
	global year_dir
	year_data = np.load(year_dir + str(year)+ '.npy', allow_pickle = True).item()
	features_dict = {}
	
	for lat in year_data['latitudes']:
		for lon in year_data['longitudes']:
			features_dict['{}_{}'.format(lat, lon)] = {'X': [], 'y': []}
	
	
	
	for month in range(len(year_data['sst'])):
		for n_row in range(len(year_data['sst'][month])):
			for n_tile in range(len(year_data['sst'][month][n_row])):
				lat = year_data['latitudes'][n_row]
				lon = year_data['longitudes'][n_tile]
				temp_xai = []
				for feature in X_vars:
					temp_xai.append(year_data[feature][month][n_row][n_tile])
				
				if True not in np.isnan(temp_xai) and True not in np.isnan([year_data[y_var][month][n_row][n_tile]]):
					features_dict['{}_{}'.format(lat, lon)]['X'].append(np.array(temp_xai))
					features_dict['{}_{}'.format(lat, lon)]['y'].append(year_data[y_var][month][n_row][n_tile])
	
	remove = []
	for key in features_dict.keys():
		if len(features_dict[key]['X']) < 10:
			remove.append(key)
	for key in remove:
		del features_dict[key]
	
	return features_dict
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
		


					
		
