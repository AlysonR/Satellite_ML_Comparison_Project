import numpy as np
import subprocess
import sys
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import tools

def get_file(year, month, modis_lats, modis_lons):
	merra_dict = {}
	remove_string = 'rm {}'
	call_string= 'curl -n -c ~/.urs_cookies -b ~/.urs_cookies -LJO --url {}'
	#url_aero = 'https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2_DIURNAL/M2TUNXAER.5.12.4/{}/MERRA2_300.tavgU_2d_aer_Nx.{}{}.nc4'.format(year, year, month)
	url_aero = 'https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2_MONTHLY/M2TMNXAER.5.12.4/{}/MERRA2_300.tavgM_2d_aer_Nx.{}{}.nc4'.format(year, year, month)
	url_3d = 'https://goldsmr3.gesdisc.eosdis.nasa.gov/data/MERRA_MONTHLY/MAIMNPANA.5.2.0/{}/MERRA300.prod.assim.instM_3d_ana_Np.{}{}.hdf'.format(year, year, month)
	url_1d = 'https://goldsmr2.gesdisc.eosdis.nasa.gov/data/MERRA_MONTHLY/MATMNXSLV.5.2.0/{}/MERRA300.prod.assim.tavgM_2d_slv_Nx.{}{}.hdf'.format(year, year, month)
	print('Getting aerosol')
	subprocess.call(call_string.format(url_aero).split())
	print('Getting 3d meteorology')
	subprocess.call(call_string.format(url_3d).split())
	print('Getting 1d meteorology')
	subprocess.call(call_string.format(url_1d).split())
	
	aerosol_name = 'MERRA2_300.tavgM_2d_aer_Nx.{}{}.nc4'.format(year, month)
	met_3d_name = 'MERRA300.prod.assim.instM_3d_ana_Np.{}{}.hdf'.format(year, month)
	met_1d_name = 'MERRA300.prod.assim.tavgM_2d_slv_Nx.{}{}.hdf'.format(year, month)
	################################################
	
	aerosol_data = Dataset(aerosol_name, 'r')
	aerosol_lats = aerosol_data['lat'][:]
	aerosol_lons = aerosol_data['lon'][:]
	
	merra_dict['bc_ang'] = aerosol_data['BCANGSTR'][:][0]
	merra_dict['bc_aod'] = aerosol_data['BCEXTTAU'][:][0]
	merra_dict['bc_ai'] = merra_dict['bc_ang'] * merra_dict['bc_aod']
	
	merra_dict['du_ang'] = aerosol_data['DUANGSTR'][:][0]
	merra_dict['du_aod'] = aerosol_data['DUEXTTAU'][:][0]
	merra_dict['du_ai'] = merra_dict['du_aod'] * merra_dict['du_ang']
	
	merra_dict['oc_ang'] = aerosol_data['OCANGSTR'][:][0]
	merra_dict['oc_aod'] = aerosol_data['OCEXTTAU'][:][0]
	merra_dict['oc_ai'] = merra_dict['oc_aod'] * merra_dict['oc_ang']
	
	merra_dict['su_ang'] = aerosol_data['SUANGSTR'][:][0]
	merra_dict['su_aod'] = aerosol_data['SUEXTTAU'][:][0]
	merra_dict['su_ai'] = merra_dict['su_ang'] * merra_dict['su_aod']
	
	merra_dict['ss_ang'] = aerosol_data['SSANGSTR'][:][0]
	merra_dict['ss_aod'] = aerosol_data['SSEXTTAU'][:][0]
	merra_dict['ss_ai'] = merra_dict['ss_aod'] * merra_dict['ss_ang']
	
	merra_dict['tot_ang'] = aerosol_data['TOTANGSTR'][:][0]
	merra_dict['tot_aod'] = aerosol_data['TOTEXTTAU'][:][0]
	merra_dict['tot_ai'] = merra_dict['tot_ang'] * merra_dict['tot_aod']
	
	subprocess.call(remove_string.format(aerosol_name).split())
	
	################################################
	
	met_3d_data = Dataset(met_3d_name, 'r')
	
	merra_lats = met_3d_data['YDim'][:]
	merra_lons = met_3d_data['XDim'][:]
	heights = met_3d_data['Height'][:].tolist()
	i_700 = heights.index(700.)
	i_500 = heights.index(500.)
	i_850 = heights.index(850.)
	i_250 = heights.index(250.)
	
	surface_pres = met_3d_data['PS'][:][0]
	temps = met_3d_data['T'][:][0]
	spec_humidity = met_3d_data['QV'][:][0]
	
	U_profile = met_3d_data['U'][:][0]
	V_profile = met_3d_data['V'][:][0]
	
	subprocess.call(remove_string.format(met_3d_name).split())
	
	################################################
	
	met_1d_data = Dataset(met_1d_name, 'r')
	
	merra_dict['w500'] = met_1d_data['OMEGA500'][:][0]
	surface_temps = met_1d_data['TS'][:][0]
	
	subprocess.call(remove_string.format(met_1d_name).split())
	
	################################################
	
	find_LTS = np.vectorize(tools.find_LTS)
	merra_dict['LTS'] = find_LTS(surface_temps, temps[i_700, :, :], surface_pres)
	merra_dict['upper_level_U'] = U_profile[i_250, :, :]
	merra_dict['upper_level_V'] = V_profile[i_250, :, :]
	merra_dict['upper_level_winds'] = np.sqrt(merra_dict['upper_level_U'] **2 + merra_dict['upper_level_V'] ** 2)
	
	merra_dict['U_850'] = U_profile[i_850, :, :]
	merra_dict['V_850'] = V_profile[i_850, :, :]
	
	merra_dict['U_500'] = U_profile[i_500, :, :]
	merra_dict['V_500'] = V_profile[i_500, :, :]
	
	find_RH = np.vectorize(tools.find_rh)
	merra_dict['RH850'] = find_RH(spec_humidity[i_850, :, :], 85000., temps[i_850, :, :])
	merra_dict['RH700'] = find_RH(spec_humidity[i_700, :, :], 70000., temps[i_700, :, :])
	
	################################################
	
	for variable in merra_dict.keys():
		if merra_dict[variable].shape == (361, 576):
			merra_dict[variable] = tools.interp(merra_dict[variable], aerosol_lats, aerosol_lons, modis_lats, modis_lons)	
		else:
			merra_dict[variable] = tools.interp(merra_dict[variable], merra_lats, merra_lons, modis_lats, modis_lons)	
		
	return merra_dict
