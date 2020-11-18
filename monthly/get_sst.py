import numpy as np
import subprocess
import sys
from pyhdf.SD import SD, SDC
import glob
import matplotlib.pyplot as plt
sys.path.append('/home/users/rosealyd/ML_sat_obs/')
import get_SST
import tools

def get_sst_airs(year, month):
	
	remove_string = 'rm {}'
	call_string= 'curl -n -c ~/.urs_cookies -b ~/.urs_cookies -LJO --url {}'
	ssts_dict = np.load('sst_urls.npy', allow_pickle = True).item()
	url_sst = ssts_dict[int(month)]
	sst_name = glob.glob('*')
	print('getting sst data')
	#subprocess.call(call_string.format(url_sst).split())
	print(glob.glob('*'))
	#sst_name =  [a for a in glob.glob('*') if a not in sst_name][0]
	print(sst_name)
	
	sst_data = SD('AIRS.2007.01.01.L3.RetStd_IR031.v6.0.9.0.G13310122101.hdf', SDC.READ)
	latitudes = sst_data.select('Latitude').get()
	longitudes = sst_data.select('Longitude').get()
	landseamask = sst_data.select('LandSeaMask').get()
	for var in sst_data.datasets():
		print(var)
	ascending_T = sst_data.select('SurfAirTemp_A').get()
	descending_T = sst_data.select('SurfAirTemp_D').get()
	print(ascending_T.shape)
	plt.subplot(121)
	plt.pcolormesh(longitudes, latitudes, ascending_T)
	plt.subplot(122)
	plt.pcolormesh(longitudes, latitudes, descending_T)
	plt.show()
	#sst = sst_data['
	sys.exit()
	return

def get_sst_avhrr(year, month, modis_lats, modis_lons):
	import calendar
	import datetime
	days_in_month = calendar.monthrange(int(year), int(month))
	month_mean = []
	for day in range(1, days_in_month[-1] + 1):
		day = datetime.date(year = int(year), month = int(month), day = int(day)).strftime('%d')
		ssts, lats, lons = get_SST.find_sst(day, month, year, return_early = True)
		month_mean.append(ssts.reshape(lats.shape[0], lons.shape[0]))
		
	mean_sst = np.nanmean(month_mean, axis = 0)
	
	lons = lons - 180.
	lats = lats - 90.
	
	mean_sst = tools.interp(mean_sst, lats, lons, modis_lats, modis_lons)
	ice = (mean_sst < 230)
	mean_sst[ice] = np.nan
	return mean_sst
	
	
	
