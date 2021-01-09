import numpy as np
import subprocess
import sys
from netCDF4 import Dataset
from pyhdf.SD import SD, SDC
import matplotlib.pyplot as plt
import tools



def get_file(year, month, modis_lats, modis_lons):
	merra_dict = {}
	remove_string = 'rm {}'
	call_string= 'curl -n -c ~/.urs_cookies -b ~/.urs_cookies -LJO --url {}'
	#url_aero = 'https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2_DIURNAL/M2TUNXAER.5.12.4/{}/MERRA2_300.tavgU_2d_aer_Nx.{}{}.nc4'.format(year, year, month)
	if int(year) > 2010:
		url_aero = 'https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2_MONTHLY/M2TMNXAER.5.12.4/{}/MERRA2_400.tavgM_2d_aer_Nx.{}{}.nc4'.format(year, year, month)
		aerosol_name = 'MERRA2_400.tavgM_2d_aer_Nx.{}{}.nc4'.format(year, month)
	else:
		url_aero = 'https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2_MONTHLY/M2TMNXAER.5.12.4/{}/MERRA2_300.tavgM_2d_aer_Nx.{}{}.nc4'.format(year, year, month)
		aerosol_name = 'MERRA2_300.tavgM_2d_aer_Nx.{}{}.nc4'.format(year, month)
	url_3d = 'https://goldsmr3.gesdisc.eosdis.nasa.gov/data/MERRA_MONTHLY/MAIMNPANA.5.2.0/{}/MERRA300.prod.assim.instM_3d_ana_Np.{}{}.hdf'.format(year, year, month)
	url_1d = 'https://goldsmr2.gesdisc.eosdis.nasa.gov/data/MERRA_MONTHLY/MATMNXSLV.5.2.0/{}/MERRA300.prod.assim.tavgM_2d_slv_Nx.{}{}.hdf'.format(year, year, month)
	url_pbl = 'https://goldsmr1.gesdisc.eosdis.nasa.gov/data/MERRA_MONTHLY/MATMFXCHM.5.2.0/{}/MERRA300.prod.assim.tavgM_2d_chm_Fx.{}{}.hdf'.format(year, year, month)
	print('Getting aerosol', url_aero)
	subprocess.call(call_string.format(url_aero).split())
	print('Getting 3d meteorology', url_3d)
	subprocess.call(call_string.format(url_3d).split())
	print('Getting 1d meteorology', url_1d)
	subprocess.call(call_string.format(url_1d).split())
	print('Getting PBL height', url_pbl)
	subprocess.call(call_string.format(url_pbl).split())
	
	
	met_3d_name = 'MERRA300.prod.assim.instM_3d_ana_Np.{}{}.hdf'.format(year, month)
	met_1d_name = 'MERRA300.prod.assim.tavgM_2d_slv_Nx.{}{}.hdf'.format(year, month)
	met_pbl_name = 'MERRA300.prod.assim.tavgM_2d_chm_Fx.{}{}.hdf'.format(year, month)
	################################################
	print(aerosol_name)
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
	print(met_3d_name)
	met_3d_data = SD(met_3d_name, SDC.READ)
	
	merra_lats = met_3d_data.select('YDim').get()
	merra_lons = met_3d_data.select('XDim').get()
	
	heights = met_3d_data.select('Height').get().tolist()
	i_700 = heights.index(700.)
	i_500 = heights.index(500.)
	i_850 = heights.index(850.)
	i_250 = heights.index(250.)
	i_1000 = 0
	
	heights_m = met_3d_data.select('H').get()[0]
	surface_pres = met_3d_data.select('PS').get()[0]
	temps = met_3d_data.select('T').get()[0]
	spec_humidity = met_3d_data.select('QV').get()[0]
	
	U_profile = met_3d_data.select('U').get()[0]
	V_profile = met_3d_data.select('V').get()[0]
	
	subprocess.call(remove_string.format(met_3d_name).split())
	
	################################################
	
	met_1d_data = SD(met_1d_name, SDC.READ)
	
	merra_dict['w500'] = met_1d_data.select('OMEGA500').get()[0]
	surface_temps = met_1d_data.select('TS').get()[0]
	bad = (surface_temps > 500)
	surface_temps[bad] = np.nan
	
	subprocess.call(remove_string.format(met_1d_name).split())
	
	################################################
	
	met_pbl_data = SD(met_pbl_name, SDC.READ)
	
	pbl_lons = met_pbl_data.select('XDim').get()
	pbl_lats = met_pbl_data.select('YDim').get()
	
	pbl_heights = met_pbl_data.select('PBLH').get()[0]
	pbl_heights = tools.interp(pbl_heights, pbl_lats, pbl_lons, merra_lats, merra_lons)
	evap = met_pbl_data.select('EVAP').get()[0]
	pbl_tops = tools.interp(met_pbl_data.select('PBLTOP').get()[0], pbl_lats, pbl_lons, merra_lats, merra_lons)
	
	subprocess.call(remove_string.format(met_pbl_name).split())
	
	################################################
	
	find_LTS = np.vectorize(tools.find_LTS)
	merra_dict['LTS'] = find_LTS(surface_temps, temps[i_700, :, :], surface_pres)

	merra_dict['u250'] = U_profile[i_250, :, :]
	merra_dict['v250'] = V_profile[i_250, :, :]
	merra_dict['upper_level_winds'] = np.sqrt(merra_dict['upper_level_U'] **2 + merra_dict['upper_level_V'] ** 2)
	
	merra_dict['U_850'] = U_profile[i_850, :, :]
	merra_dict['V_850'] = V_profile[i_850, :, :]
	
	merra_dict['U_500'] = U_profile[i_500, :, :]
	merra_dict['V_500'] = V_profile[i_500, :, :]
	
	merra_dict['U_700'] = U_profile[i_700, :, :]
	merra_dict['V_700'] = V_profile[i_700, :, :]
	merra_dict['winds_700'] = np.sqrt(merra_dict['U_700']**2 + merra_dict['V_700']**2)
	
	find_RH = np.vectorize(tools.find_rh)
	merra_dict['RH850'] = find_RH(spec_humidity[i_850, :, :], 85000., temps[i_850, :, :])
	merra_dict['RH700'] = find_RH(spec_humidity[i_700, :, :], 70000., temps[i_700, :, :])
	RH_surface = find_RH(spec_humidity[i_1000, :, :], surface_pres, surface_temps)
	
	EIS = np.full(surface_temps.shape, 1000000.)
	for i in range(len(EIS)):
		for j in range(len(EIS[i])):
			EIS[i][j] = tools.find_EIS(surface_temps[i, j], temps[i_700, i, j], surface_pres[i, j], RH_surface[i, j], heights_m[i_700, i, j], temps[:, i, j], heights_m[:, i, j], heights, pbl_heights[i, j])
	EIS = tools.interp(EIS, merra_lats, merra_lons, modis_lats, modis_lons)
		
	################################################
	
	
	for variable in merra_dict.keys():
		if merra_dict[variable].shape == (361, 576):
			merra_dict[variable] = tools.interp(merra_dict[variable], aerosol_lats, aerosol_lons, modis_lats, modis_lons)	
		else:
			merra_dict[variable] = tools.interp(merra_dict[variable], merra_lats, merra_lons, modis_lats, modis_lons)	
	merra_dict['EIS'] = EIS
	for var in merra_dict.keys():
		bad = (merra_dict[var] > 100000)
		merra_dict[var][bad] = np.nan
	
	return merra_dict
