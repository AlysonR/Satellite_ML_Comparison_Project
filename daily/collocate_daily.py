import numpy as np
import get_daily_MODIS
import datetime
import get_merra
import matplotlib.pyplot as plt
import get_SST
from calendar import monthrange
import get_ecmwf


start_year = 2003
end_year = 2004
for year in range(start_year, end_year + 1):
	for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:

		monthly_dict = {'cwp': [], 'iwp': [], 'cth': [], 'cod': [], 'l_re': [], 'i_re': [], 'cf': [], 'modis_aod': [], 
		'EIS': [], 'LTS': [], 'w500': [], 'u500': [], 'v500': [], 'u850': [], 'v850': [], 'u700': [], 'v700': [], 'usfc': [], 
		'vsfc': [], 'RH900': [], 'RH850': [], 'RH700': [], 'evap': [], 'sens_h': [], 'latent_h': [], 'su_ai': [], 'su_aod': [],
		'du_ai': [], 'du_aod': [], 'oc_ai': [], 'oc_aod': [], 'bc_ai': [], 'bc_aod': [], 'ss_ai': [], 'ss_aod': [], 
		'tot_ai': [], 'tot_aod': [], 'tot_ang': [], 'sst': [], 'u250': [], 'v250': [], 'upper_level_winds': [], 
		'ml_ice_frac': [], 'ml_liq_frac': [], 'ml_frac': [], 'd_ctoaer': [], 't2': [], 'CAPE': []}
		merra_keys = ['EIS', 'LTS', 'w500', 'u500', 'v500', 'u850', 'v850', 'u700', 'v700', 'usfc', 'vsfc', 'RH900', 'RH850', 'RH700', 'evap', 'sens_h', 'latent_h','su_ai', 'su_aod', 'du_ai', 'du_aod', 'oc_ai', 'oc_aod', 'bc_ai', 'bc_aod', 'ss_ai', 'ss_aod', 'tot_ai', 'tot_ang', 'tot_aod', 'u250', 'v250', 'upper_level_winds']
	
		for n in range(1, monthrange(int(year), int(month))[-1] + 1):
			day = datetime.date(year = int(year), month = int(month), day = n).strftime('%d')
			try:
				mo_lats, mo_lons, modis_dict = get_daily_MODIS.get_day(year, month, day)
			except IndexError:
				print('\n')
				print('no MODIS, skipping', day)
				print('\n')
				continue
			for key in modis_dict.keys():
				monthly_dict[key].append(modis_dict[key])
			merra_dict = get_merra.get_daily(year, month, day, mo_lats, mo_lons)
			for key in merra_keys:
				monthly_dict[key].append(merra_dict[key])
			
			monthly_dict['sst'].append(get_SST.find_sst(year, month, day, mo_lats, mo_lons))
			cape, temp2 = get_ecmwf.get_ecmwf(year, month, day)
			monthly_dict['t2'].append(temp2)
			monthly_dict['CAPE'].append(cape)
			
			monthly_dict['lats'] = mo_lats
			monthly_dict['lons'] = mo_lons
		
		np.save('/gws/nopw/j04/aopp/douglas/{}_{}_test'.format(month, year), monthly_dict)
	
