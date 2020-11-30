import numpy as np
import glob
import sys

def get_single_X_y(X_vars, y_var, year):
	months = glob.glob('*_{}_test.npy'.format(year))
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
	print(np.array(features_dict['1.5_1.5']['X']).shape)
	
	sys.exit()


get_single_X_y(['EIS', 'sst', 'tot_ang', 'tot_aod'], 'cf', 2007)

