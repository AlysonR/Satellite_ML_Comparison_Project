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
	print(year_data.keys())
	sys.exit()
	for var in X_vars:
		temp = []
		for month in year_data[var]:
			test = month.ravel()
			temp.extend(test)
		xais.append(temp)
	print(np.array(xais).shape)
	
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


def plot_year(predictor, X_vars, y_var, year, GCM = False, GCM_data = None):
	global year_dir
	if GCM:
		year_data = GCM_data
	else:
		year_data = np.load(year_dir + str(year) + '.npy', allow_pickle = True).item()
	pred_y = np.zeros(year_data[y_var][0].shape)
	
	for month in range(len(year_data['LTS'])):
		print(month)
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
		over = (pred_y > 1.)
		pred_y[over] = 1.
		print(np.nanmean(pred_y), 'predicted mean')
		print(np.nanmean(year_data['cf'][month]), 'actual mean')
		plt.subplot(121)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], pred_y, vmin = 0, vmax = 1.)
		plt.title('Predicted CF')
		plt.colorbar()
		plt.subplot(122)
		plt.pcolormesh(year_data['longitudes'], year_data['latitudes'], year_data['cf'][month], vmin = 0, vmax = 1)
		plt.title('MODIS Monthly CF')
		plt.colorbar()
		plt.show()
		sys.exit()
					
		
