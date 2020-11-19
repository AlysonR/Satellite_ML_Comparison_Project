import numpy as np
import sys
import matplotlib.pyplot as plt

year_dir = '/home/users/rosealyd/ML_sat_obs/monthly/'

def get_as_X_y(X_vars, y_var, year):
	global year_dir
	year_data = np.load(year_dir + str(year)+ '.npy', allow_pickle = True).item()
	xais = []
	yais = []
	X_vars.append(y_var)
	
	for var in X_vars:
		temp = []
		for month in year_data[var]:
			if var == 'sst':
				month = np.rot90(np.transpose(month))
			test = month.ravel()
			temp.extend(test)
		xais.append(temp)
	
	if len(xais) == 6:
		xais = [items for items in zip(xais[0], xais[1], xais[2], xais[3], xais[4], xais[-1]) if True not in np.isnan(list(items))]
	if len(xais) == 7:
		xais = [items for items in zip(xais[0], xais[1], xais[2], xais[3], xais[4], xais[5], xais[-1]) if True not in np.isnan(list(items))]
	if len(xais) == 8:
		xais = [items for items in zip(xais[0], xais[1], xais[2], xais[3], xais[4], xais[5], xais[6], xais[-1]) if True not in np.isnan(list(items))]
	xais = np.array(xais)
	
	ys = xais[:, -1]
	xais = xais[:, :-1]
	
	X_vars.pop(-1)
	
	return xais, ys, X_vars, [year_dir + str(year)]


def plot_year(predictor, X_vars, y_var, year):
	global year_dir
	year_data = np.load(year_dir + str(year) + '.npy', allow_pickle = True).item()
	pred_y = np.zeros(year_data[y_var][0].shape)
	
	for month in range(len(year_data['LTS']))[:1]:
		print(month)
		year_data['sst'][month] = np.rot90(np.transpose(year_data['sst'][month]))
		for lat_row in range(len(year_data['LTS'][month])):
			for lon_tile in range(len(year_data['LTS'][month][lat_row])):
				xai = []
				for var in X_vars:
					xai.append(year_data[var][month][lat_row][lon_tile])
				if True in np.isnan(xai):
					pred_y[lat_row][lon_tile] = np.nan
				else:
					pred_y[lat_row][lon_tile] = predictor.predict([xai])[0]
		land = np.isnan(pred_y)
		year_data['cf'][month][land] = np.nan
		print(np.nanmean(pred_y), 'predicted mean')
		print(np.nanmean(year_data['cf'][month]), 'actual mean')
		plt.subplot(121)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], pred_y)
		plt.title('Predicted CF')
		plt.colorbar()
		plt.subplot(122)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], year_data['cf'][month], vmin = 0, vmax = 1)
		plt.title('MODIS Monthly CF')
		plt.colorbar()
		plt.show()
		sys.exit()
					
		
