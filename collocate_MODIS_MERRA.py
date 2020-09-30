import numpy as np
from sklearn.neighbors import KDTree
import matplotlib.pyplot as plt
import load_l2_MODIS
import datetime
import glob

merra_dir = '/gws/nopw/j04/eo_shared_data_vol1/reanalysis/MERRA-2/'

modis_day = '002'
modis_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/myd06_l2/2007/{}/'

merra_hours = np.array([0, 6, 12, 18, 24])

#first get the modis data
modis_daily = glob.glob(modis_dir.format(modis_day) + '*.hdf')
modis_dict = {}
for filename in modis_daily:
	warm_frac, all_frac, lat_lon_dict = load_l2_MODIS.get_cloud_fraction(filename, average = True, local_grid = True, local_space = 2.5)
	print(lat_lon_dict)
	hour = int(filename.split('/')[-1].split('.')[2][:2])
	#minute = filename.split('/')[-1].split('.')[2][2:]
	corr_merra_t = np.abs(merra_hours - hour).argmin()
	if corr_merra_t == 4:
		modis_day = int(modis_day) + 1
		corr_merra_t = 0
	date = datetime.date(2007, 1, 1) + datetime.timedelta(days = int(modis_day) -1)
	merra_filename = merra_dir + date.strftime('%d_%m_%Y.npy')
	merra_data = np.load(merra_filename).item()
	
	
	
