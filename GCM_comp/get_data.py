import numpy as np
import glob
import tools
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/users/rosealyd/get_MERRA/')
import src
import pickle

c_EIS = True
c_ltss = False

def get_data(bld_dir, sst_dir, t_dir, ps_dir, rh_dir, spechum_dir, omega_dir, u_dir, v_dir, cf_dir, surf_t_dir, surf_p_dir, zs_dir, a550_dir, aod870_dir, aod440_dir):
	ssts = []
	seasurfaces = []
	ts = []
	ps = []
	t_profs = []
	t700s = []
	ps = []
	rh_profs = []
	rh700s = []
	rh850s = []
	omegas = []
	z700s = []
	
	u250s = []
	v250s = []
	u500s = []
	v500s = []
	all_cf = []
	spec_hum_profs = []
	spec_hum_levs = []
	
	aod550 = []
	aod870 = []
	aod440 = []
	angstrom = []
	rh_surf = []
	lclps = []
	lclzs = []
	lclts = []
	tprofs = []
	eiss = []
	ltss = []
	
	
	
	for filename in sorted(glob.glob(surf_p_dir + '*.nc'))[:1]:
		ps_data = Dataset(filename, 'r')
		ps.extend(ps_data['ps'][:])
		ps_data.close()
	
	for filename in sorted(glob.glob(surf_t_dir + '*.nc'))[:1]:
		surf_data = Dataset(filename, 'r')
		ts.extend(surf_data['ts'][:])
		surf_data.close()
	ts = np.array(ts)
	for filename in sorted(glob.glob(zs_dir + '*.nc'))[:1]:
		height_data = Dataset(filename, 'r')
		heights_levs = height_data['plev'][:].tolist()
		i700 = heights_levs.index(70000.)
		heights = height_data['zg'][:]
		z700s.extend(heights[:, i700, :, :])
		height_data.close()
	
	for filename in sorted(glob.glob(rh_dir + '*.nc'))[:1]:
		rh_data = Dataset(filename, 'r')
		rh_prof = rh_data['hur'][:]
		heights_pa = rh_data['plev'][:].tolist()
		i_1000 = heights_pa.index(100000.)
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
		relhum = rh_prof[:, i_1000, :, :]
		bad = (relhum > 1000)
		relhum[bad] = np.nan
		rh_surf.extend(relhum)
		rh_data.close()
	#put these in decimal units
	rh700s = np.array(rh700s)
	rh850s = np.array(rh850s)
	rh_surf = np.array(rh_surf)
	
	for filename in sorted(glob.glob(t_dir + '*.nc'))[:1]:
		temp_data = Dataset(filename, 'r')
		ta = temp_data['ta'][:]
		heights_pa = temp_data['plev'][:].tolist()
		i700 = heights_pa.index(70000.)
		i500 = heights_pa.index(50000.)
		bad = (ta > 350)
		ta[bad] = np.nan
		t700s.extend(ta[:, i700, :, :])	
		tprofs.extend(ta[:, :, :, :])
		temp_data.close()
	t700s = np.array(t700s)
	plevs = np.array(heights_pa)
	tprofs = np.array(tprofs)
	print('calcing eis')
	if c_EIS:
		pbl_hs = calc_pbl(bld_dir)
		calc_lcl = np.vectorize(src.find_LCL)
		calc_p = np.vectorize(src.find_p)
		calc_EIS = np.vectorize(src.find_EIS)
		#for month in range(ts.shape[0]):
		for month in range(10):
			lcl = calc_lcl(ts[month], rh_surf[month])
			lclp = calc_p(ts[month], ps[month], lcl)
			
			monthly_lclts = np.empty(lcl.shape)
		
			for row in range(lclp.shape[0]):
				for p in range(lclp.shape[1]):
					if not np.isnan(lclp[row][p]):
						temp = plevs - lclp[row][p]
						i = np.argmin(temp)
						lclt = tprofs[month, i, row, p]
						monthly_lclts[row][p] = lclt
				
			
			lclts.append(monthly_lclts)
			lclps.append(lclp)
			lclzs.extend(lcl)
		
			eis = calc_EIS(ts[month], t700s[month], ps[month], lcl, z700s[month], monthly_lclts, lclp, pbl_hs[month], rh_surf[month])
			
			eiss.append(eis)
		with open('eiss_hadgem.p', 'wb') as f:
			pickle.dump(eiss, f)
	else:
		with open('/home/users/rosealyd/ML_sat_obs/GCM_comp/eiss_hadgem.p', 'rb') as f:
			eiss = pickle.load(f)
	if c_ltss:
		calc_ltss = np.vectorize(src.find_LTS)
		for month in range(ts.shape[0]):
			temp_LTS = calc_ltss(ts[month], t700s[month], ps[month])
			ltss.append(temp_LTS)
		ltss = np.array(ltss)
		print(ltss.shape)
		with open('ltss_hadgem.p', 'wb') as f:
			pickle.dump(ltss, f)
		sys.exit()
	else:
		with open('/home/users/rosealyd/ML_sat_obs/GCM_comp/ltss_hadgem.p', 'rb') as f:
			ltss = pickle.load(f)
	for filename in sorted(glob.glob(spechum_dir + '*.nc'))[:1]:
		spechum_data = Dataset(filename, 'r')
		spec_prof = spechum_data['hus'][:]
		spechum_ps = spechum_data['plev'][:]
		spec_hum_profs.append(spec_prof)
		spec_hum_levs.append(spechum_ps)
	
	for filename in sorted(glob.glob(cf_dir + '*.nc'))[:1]:
		cf_data = Dataset(filename, 'r')
		cloudfractions = cf_data['clt'][:]
		bad = (cloudfractions > 10000)
		cloudfractions[bad] = np.nan
		all_cf.extend(cloudfractions/100.)
	all_cf = np.array(all_cf)
	
	for filename in sorted(glob.glob(u_dir + '*.nc'))[:1]:
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
	
	for filename in sorted(glob.glob(v_dir + '*.nc'))[:1]:
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
	
	for filename in glob.glob(omega_dir + '*.nc')[:1]:
		omega_data = Dataset(filename, 'r')
		lats = omega_data['lat'][:]
		lons = omega_data['lon'][:]
		levs = omega_data['plev'][:].tolist()
		waps = omega_data['wap'][:]
		i_500 = levs.index(50000.)
		omegas.extend(waps[:, i_500, :, :])
	omegas = np.array(omegas)
	
	#have to inerpolate since SST isnt on the same grid
	for filename in sorted(glob.glob(sst_dir + '*.nc'))[:1]:
		sst_data = Dataset(filename, 'r')
		seasurface = sst_data['tos'][:]
		bad = (seasurface > 400)
		seasurface[bad] = -100		
		seasurfaces.extend(seasurface)
		sst_data.close()
	seasurfaces = np.array(seasurfaces)
	sst_lats = np.linspace(-90, 90, seasurface.shape[1])
	sst_lons = np.linspace(0, 360, seasurface.shape[2])
	
	#must go in and do every month
	for month in range(seasurfaces.shape[0]):
		interp_sst = tools.interp(seasurfaces[month], sst_lats, sst_lons, lats, lons)
		#set to K
		interp_sst += 273.15
		bad = ((interp_sst < 258) | (interp_sst > 325))
		interp_sst[bad] = np.nan
		ssts.append(interp_sst)
		
	ssts = np.array(ssts)

	for filename in glob.glob(aod870_dir + '*.nc')[:1]:
		aod_data = Dataset(filename, 'r')
		temp_aods = aod_data['od870aer'][:]
		aod870.extend(temp_aods)
		aod_data.close()
	aod870 = np.array(aod870)
	print(aod870.shape)
	
	for filename in glob.glob(aod440_dir + '*.nc')[:1]:
		aod_data = Dataset(filename, 'r')
		temp_aods = aod_data['od440aer'][:]
		aod440.extend(temp_aods)
		aod_data.close()
	aod440 = np.array(aod440)

	calc_ang = np.vectorize(find_ang)
	for month in range(aod870.shape[0]):
		angstrom_exp = calc_ang(aod870[month], aod440[month])
		angstrom.append(angstrom_exp)
	angstrom = np.array(angstrom)

	for filename in glob.glob(a550_dir + '*.nc')[:1]:
		aod_data = Dataset(filename, 'r')
		temp_aods = aod_data['od550aer'][:]
		aod550.extend(temp_aods)
		aod_data.close()
	aod550 = np.array(aod550)
	
	
	lons = lons - 180.
	
	
	data_dict = {'latitudes': lats, 'longitudes': lons, 'cf': all_cf[:10], 'sst': ssts[:10], 'upper_level_winds': np.sqrt(v250s[:10]**2 + u250s[:10]**2), 'w500': omegas[:10], 'RH850': rh850s[:10], 'EIS': eiss[:10], 'tot_aod': aod550[:10], 'tot_ang': angstrom[:10]}
	
	
	return data_dict

def find_ang(aod_870, aod_440):
	ai = np.log(aod_870/aod_440)
	ai = ai/np.log(870/440) * -.9032474998572043
	return ai

def stack_data(stacking_dict):
	stacked_X = []
	for month in range(stacking_dict['sst'].shape[0]):
		temp_stack = []
		for var in stacking_dict.keys():
			unraveled = stacking_dict[var][month].ravel()
			temp_stack.append(unraveled)
		temp_stack = np.array(temp_stack)
		if month == 0:
			stacked_X = temp_stack
		else:
			stacked_X = np.hstack((stacked_X, temp))
	stacked_X = stacked_X[:, ~np.isnan(stacked_X).any(axis = 0)]
	truth = stacked_X[0, :]
	Xais = stacked_X[1:, :]
	print(Xais.shape)
	print(truth.shape)
	
	return truth, Xais
		
def calc_pbl(pbl_dir):
	import datetime
	import calendar
	aggregated_pbls = []
	for filename in sorted(glob.glob(pbl_dir + '*.nc'))[:1]:
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
	

