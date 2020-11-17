import numpy as np
from netCDF4 import Dataset
import glob
import sys
import matplotlib.pyplot as plt
import tools

#X_vars = ['LTS', 'sst', 'w500', 'RH850', 'tot_ai']

var_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/'
cloud_fraction_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/clt/gn/files/d20190311/'
temp_prof_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/ta/gn/files/d20190311/'
surf_temp_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/tas/gn/files/d20181212/'
rh_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/hur/gn/files/d20190311/'
sst_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Omon/tos/gn/files/d20181212/'
ps_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/ps/gn/files/d20181212/'
omegas_dir = '/badc/cmip6/data/CMIP6/CMIP/MIROC/MIROC6/historical/r10i1p1f1/Amon/wap/gn/files/d20190311/'

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
omegas = []
ltss = []

for filename in sorted(glob.glob(sst_dir + '*.nc')):
	sst_data = Dataset(filename, 'r')
	seasurface = sst_data['tos'][:]
	bad = (seasurface > 400)
	seasurface[bad] = np.nan
	ssts.extend(seasurface) 

for filename in sorted(glob.glob(rh_dir + '*.nc')):
	rh_data = Dataset(filename, 'r')
	rh_prof = rh_data['hur'][:]
	heights_pa = rh_data['plev'][:].tolist()
	i700 = heights_pa.index(85000.)
	relhum = rh_prof[:, i700, :, :]
	bad = (relhum > 10000)
	relhum[bad] = np.nan
	rh700s.extend(relhum)
rh700s = np.array(rh700s)

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

ais = np.linspace(.02, 15, 11)

calc_lts = np.vectorize(tools.find_LTS)
pred_range = []
act_range = []
X = []
for ai in ais:
#for time in range(1901, 1981):
	time = 1901
	lts = calc_lts(ts[time, :, :], t700s[time, :, :], ps[time, :, :])
	xai = np.array([(a, b, c, d, ai) for a, b, c, d  in zip(lts.ravel(), ssts[time].ravel(), omegas[time].ravel(), rh700s[time].ravel())])
	good = np.where(np.isnan(xai) == False)[0]
	xai = xai[good]
	comp_cfs = all_cf[time].ravel()[good]
	predicted_cfs = tools.predict('/home/users/rosealyd/ML_sat_obs/saved_models/xgb_train.sav', xai)
	diff = comp_cfs - predicted_cfs
	'''plt.hist2d(predicted_cfs, comp_cfs)
	plt.colorbar()
	plt.xlabel('RF derived')
	plt.ylabel('MIROC cf')
	plt.show()'''
	pred_range.append(predicted_cfs[1200])
	act_range.append(comp_cfs[1200])
	
plt.plot(ais, pred_range)
plt.plot(ais, act_range)
plt.show()






