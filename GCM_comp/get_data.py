import numpy as np
import glob
import tools
from netCDF4 import Dataset
import sys

def get_data(bld_dir, sst_dir, t_dir, ps_dir, rh_dir, spechum_dir, omega_dir, u_dir, v_dir, cf_dir):
	
	ssts = []
	ts = []
	t_profs = []
	t700s = []
	ps = []
	rh_profs = []
	rh700s = []
	rh850s = []
	omegas = []
	ltss = []
	u250s = []
	v250s = []
	u500s = []
	v500s = []
	all_cf = []
	spec_hum_profs = []
	spec_hum_levs = []
	aod550 = []
	angstrom = []
	
	pbl_hs = calc_pbl(bld_dir)
	print(pbl_hs.shape)
	
	for filename in sorted(glob.glob(cf_dir + '*.nc')):
		cf_data = Dataset(filename, 'r')
		cloudfractions = cf_data['clt'][:]
		bad = (cloudfractions > 10000)
		cloudfractions[bad] = np.nan
		all_cf.extend(cloudfractions/100.)
	all_cf = np.array(all_cf)
	latitudes = cf_data['lat']
	longitudes = cf_data['lon']
	print(all_cf.shape)
	sys.exit()
	
	for filename in sorted(glob.glob(spechum_dir + '*.nc')):
		spechum_data = Dataset(filename, 'r')
		spec_prof = spechum_data['hus'][:]
		spechum_ps = spechum_data['plev'][:]
		spec_hum_profs.append(spec_prof)
		spec_hum_levs.append(spec_ps)

	
	for filename in sorted(glob.glob(u_dir + '*.nc')):
		uwind_data = Dataset(filename, 'r')
		heights_wind = uwind_data['plev'][:].tolist()
		i250 = heights_wind.index(25000.)
		i500 = heights_wind.index(50000.)
		uwinds = uwind_data['ua'][:]
		uwinds = uwinds[:, i250, :, :]
		bad = (uwinds > 500)
		uwinds[bad] = np.nan
		u250s.extend(uwinds)
		uwinds = uwind_data['ua'][:]
		uwinds = uwinds[:, i500, :, :]
		bad = (uwinds > 500)
		uwinds[bad] = np.nan
		u500s.extend(uwinds)
		uwind_data.close()
	u250s = np.array(u250s)
	u500s = np.array(u500s)
	
	for filename in sorted(glob.glob(v_dir + '*.nc')):
		vwind_data = Dataset(filename, 'r')
		print(vwind_data.variables)
		heights_wind = vwind_data['plev'][:].tolist()
		i250 = heights_wind.index(25000.)
		i500 = heights_wind.index(50000.)
		vwinds = vwind_data['va'][:]
		vwinds = vwinds[:, i250, :, :]
		bad = (vwinds > 500)
		vwinds[bad] = np.nan
		v250s.extend(vwinds)
		vwinds = vwind_data['va'][:]
		vwinds = vwinds[:, i500, :, :]
		bad = (vwinds > 500)
		vwinds[bad] = np.nan
		v500s.extend(vwinds)
		vwind_data.close()
	v250s = np.array(v250s)
	v500s = np.array(v500s)
	
	#have to inerpolate since SST isnt on the same grid
	for filename in sorted(glob.glob(sst_dir + '*.nc')):
		sst_data = Dataset(filename, 'r')
		sst_lats = sst_data['lat'][:]
		sst_lons = sst_data['lon'][:]
		seasurface = sst_data['tos'][:]
		bad = (seasurface > 400)
		seasurface[bad] = np.nan
		#must go in and do every month
		seasurface = tools.interp2d(seasurface, sst_lats, sst_lons, latitudes, longitudes)
		ssts.extend(seasurface) 
		sst_data.close()
	ssts = np.array(ssts)
	print(ssts.shape, 'ssts shape', u250s.shape, 'normal shape')
	
	for filename in sorted(glob.glob(rh_dir + '*.nc')):
		rh_data = Dataset(filename, 'r')
		rh_prof = rh_data['hur'][:]
		heights_pa = rh_data['plev'][:].tolist()
		i700 = heights_pa.index(70000.)
		i850 = heights_pa.index(85000.)
		relhum = rh_prof[:, i700, :, :]
		bad = (relhum > 10000)
		relhum[bad] = np.nan
		rh700s.extend(relhum)
		relhum = rh_prof[:, i850, :, :]
		bad = (relhum > 10000)
		relhum[bad] = np.nan
		rh850s.extend(relhum)
		rh_data.close()
	rh700s = np.array(rh700s)
	rh850s = np.array(rh850s)
	
	
	
	return
		
def calc_pbl(pbl_dir):
	import datetime
	import calendar
	aggregated_pbls = []
	for filename in sorted(glob.glob(pbl_dir + '*.nc')):
		year = int(filename.split('/')[-1].split('gn_')[-1][:4])
		pbl_data = Dataset(filename, 'r')
		pbls = pbl_data['bldep'][:]
		monthly_pbls = []
		time = pbl_data['time'][:]
		start_date = datetime.datetime(year = year, month = 1, day = 1, hour = 3)
		datetimes = []
		for t in time:
			date = start_date + datetime.timedelta(days = t)
			datetimes.append(date)
		datetimes = np.array(datetimes)
		for month in range(1, 13):
			monthrange = calendar.monthrange(month = month, year = year)
			lastday = monthrange[-1]
			month_indices = np.where(((datetimes >= datetime.datetime(year = year, month = month, day = 1)) & (datetimes <= datetime.datetime(year = year, month = month, day = lastday))) == True)[0]
			test = np.nanmean(pbls[month_indices], axis = 0)
			monthly_pbls.append(test)
		pbl_data.close()
		aggregated_pbls.extend(monthly_pbls)
	return np.array(aggregated_pbls)
	

