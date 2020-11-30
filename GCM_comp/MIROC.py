import numpy as np
from netCDF4 import Dataset
import glob
import sys
import matplotlib.pyplot as plt
import tools
sys.path.append('/home/users/rosealyd/ML_sat_obs/monthly/')
import get_year

#X_vars = ['LTS', 'sst', 'w500', 'RH850', 'tot_ai']

var_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/'
cloud_fraction_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/clt/gn/files/d20190311/'
temp_prof_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/ta/gn/files/d20190311/'
surf_temp_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/tas/gn/files/d20181212/'
rh_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/hur/gn/files/d20190311/'
sst_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Omon/tos/gn/files/d20181212/'
ps_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/ps/gn/files/d20181212/'
omegas_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/wap/gn/files/d20190311/'
u_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/ua/gn/files/d20190311/'
v_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/va/gn/files/d20190311/'
all_cf = []

for filename in sorted(glob.glob(cloud_fraction_dir + '*.nc')):
	cf_data = Dataset(filename, 'r')
	cloudfractions = cf_data['clt'][:]
	bad = (cloudfractions > 10000)
	cloudfractions[bad] = np.nan
	all_cf.extend(cloudfractions/100.)
latitudes = cf_data['lat']
longitudes = cf_data['lon']

ssts = []
ts = []
t700s = []
ps = []
rh700s = []
rh850s = []
omegas = []
ltss = []
u250s = []
v250s = []
u500s = []
v500s = []

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
	#seasurface = tools.interp2d(seasurface, sst_lats, sst_lons, latitudes, longitudes)
	ssts.extend(seasurface) 
ssts = np.array(ssts)
print(ssts.shape)
sys.exit()
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
rh700s = np.array(rh700s)
rh850s = np.array(rh850s)
print(rh700s.shape)
print(rh840s.shape)

for filename in sorted(glob.glob(temp_prof_dir + '*.nc')):
	temp_data = Dataset(filename, 'r')
	ta = temp_data['ta'][:]
	heights_pa = temp_data['plev'][:].tolist()
	i700 = heights_pa.index(70000.)
	bad = (ta > 350)
	ta[bad] = np.nan
	t700s.extend(ta[:, i700, :, :])
t700s = np.array(t700s)

for filename in sorted(glob.glob(surf_temp_dir + '*.nc')):
	surface_temp_data = Dataset(filename, 'r')
	temps = surface_temp_data['tas'][:]
	bad = (temps > 400)
	temps[bad] = np.nan
	ts.extend(temps)
	
ts = np.array(ts)

for filename in sorted(glob.glob(ps_dir + '*.nc')):
	surf_pres_data = Dataset(filename, 'r')
	surf_pres = surf_pres_data['ps'][:]
	bad = (surf_pres > 1000000)
	surf_pres[bad] = np.nan
	ps.extend(surf_pres)
ps = np.array(ps)

for filename in sorted(glob.glob(omegas_dir + '*.nc')):
	omega_data = Dataset(filename, 'r')
	wap = omega_data['wap'][:]
	levels = omega_data['plev'][:].tolist()
	i500 = levels.index(50000.)
	omega500 = wap[:, i500, :, :]
	bad = (omega500 > 10000000)
	omega500[bad] = np.nan
	omegas.extend(omega500)
omegas = np.array(omegas)

ais = np.linspace(.5, 3, 11)

calc_lts = np.vectorize(tools.find_LTS)
pred_range = []
act_range = []
X = []
X_vars = ['LTS', 'sst', 'RH700', 'modis_aod', 'upper_level_U', 'upper_level_V', 'w500']
for ai in ais:
#for time in range(1901, 1981):
	time = 1901
	lts = calc_lts(ts[time, :, :], t700s[time, :, :], ps[time, :, :])
	#xai = np.array([(a, b, c, d, ai) for a, b, c, d  in zip(lts.ravel(), ssts[time].ravel(), omegas[time].ravel(), rh700s[time].ravel())])
	lgbm = tools.predict('/home/users/rosealyd/ML_sat_obs/saved_models/lightgbm_latest.sav', None, return_model = True)
	get_year.plot_year(lgbm, X_vars, 'cf', None, GCM = True, GCM_data = {'sst': [ssts[time]], 'LTS': [lts[time]], 'RH700': [rh700s[time]], 'modis_aod': [np.full(lts.shape, ai)], 'upper_level_U': [u250s[time]], 'upper_level_V': [v250s[time]], 'w500': [omegas[time]]})
	xai = np.array([(a, b, c, ai, d, e, f) for a, b, c, d, e, f in zip(lts.ravel(), ssts[time].ravel(), rh700s[time].ravel(), u250s[time].ravel(), v250s[time].ravel(), omegas[time].ravel())])
	good = np.where(np.isnan(xai) == False)[0]
	xai = xai[good]
	comp_cfs = all_cf[time].ravel()[good]
	predicted_cfs = tools.predict('/home/users/rosealyd/ML_sat_obs/saved_models/lightgbm_latest.sav', xai)
	diff = comp_cfs - predicted_cfs
	plt.hist2d(predicted_cfs, comp_cfs)
	plt.colorbar()
	plt.xlabel('RF derived')
	plt.ylabel('MIROC cf')
	plt.show()
	pred_range.append(predicted_cfs[1400])
	act_range.append(comp_cfs[1400])
	
plt.plot(ais, pred_range)
plt.plot(ais, act_range)
plt.show()





