import glob
import datetime
from pyhdf.SD import SD, SDC
import matplotlib.pyplot as plt
import sys
import numpy as np

alpha = .25

modis_daily_dir = '/gws/nopw/j04/eo_shared_data_vol1/satellite/modis/modis_c61/mod08_d3/'

def get_day(year, month, day):
	global alpha, modis_daily_dir
	
	date = datetime.date(year = int(year), month = int(month), day = int(day))
	diy = date.strftime('%j')
	filename = glob.glob(modis_daily_dir + '*A{}{}*.hdf'.format(year, diy))[0]
	print(filename)
	
	modis_data = SD(filename, SDC.READ)
	
	modis_latitudes = modis_data.select('YDim').get()
	modis_longitudes = modis_data.select('XDim').get()
	
	cwp = modis_data.select('Cloud_Water_Path_Liquid_Mean').get().astype(float)
	bad = (cwp < -1)
	cwp[bad] = np.nan
	iwp = modis_data.select('Cloud_Water_Path_Ice_Mean').get().astype(float)
	bad = (iwp < -1)
	iwp[bad] = np.nan
	
	cth = modis_data.select('Cloud_Top_Height_Mean').get().astype(float)
	bad = (cth < -1)
	cth[bad] = np.nan
	#change to km
	cth = cth/1000.
	#in the future may want to look at diurnal variation
	#cth_day = modis_data.select('Cloud_Top_Height_Day_Mean').get()
	#cth_night = modis_data.select('Cloud_Top_Height_Night_Mean').get()
	
	cod_attrs = modis_data.select('Cloud_Optical_Thickness_Combined_Mean').attributes()
	cod = modis_data.select('Cloud_Optical_Thickness_Combined_Mean').get().astype(float) * cod_attrs['scale_factor']
	bad = (cod < -1)
	cod[bad] = np.nan
	
	l_attrs = modis_data.select('Cloud_Effective_Radius_Liquid_Mean').attributes()
	l_re = modis_data.select('Cloud_Effective_Radius_Liquid_Mean').get().astype(float) * l_attrs['scale_factor']
	bad = (l_re < -1)
	l_re[bad] = np.nan
	
	
	#microns
	i_attrs = modis_data.select('Cloud_Effective_Radius_Ice_Mean').attributes()
	i_re = modis_data.select('Cloud_Effective_Radius_Ice_Mean').get().astype(float) * i_attrs['scale_factor']
	bad = (i_re < -1)
	i_re[bad] = np.nan
	
	cf_name = 'Cloud_Retrieval_Fraction_Combined'
	cf_attrs = modis_data.select(cf_name).attributes()
	cf = (modis_data.select(cf_name).get().astype(float) * cf_attrs['scale_factor']) - cf_attrs['add_offset']
	bad = (cf < 0)
	cf[bad] = np.nan
	
	dis_c_aer = modis_data.select('Aerosol_Avg_Cloud_Distance_Land_Ocean_Pixel_Counts').get().astype(float)
	bad = (dis_c_aer < -1)
	dis_c_aer[bad] = np.nan
	
	ml_frac = modis_data.select('ML_Fraction_Combined').get().astype(float)
	bad = (ml_frac < -1)
	ml_frac[bad] = np.nan
	ml_ice_frac = modis_data.select('ML_Fraction_Ice_Pixel_Counts').get().astype(float)
	bad = (ml_ice_frac < -1)
	ml_ice_frac[bad] = np.nan
	ml_liq_frac = modis_data.select('ML_Fraction_Liquid_Pixel_Counts').get().astype(float)
	bad = (ml_liq_frac < -1)
	ml_liq_frac[bad] = np.nan
	
	
	aod_attrs = modis_data.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean').attributes()
	aod = modis_data.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean').get().astype(float) * aod_attrs['scale_factor']
	bad = (aod < 0)
	aod[bad] = np.nan
	
	cdnc = (cod / ((cwp ** (5/6)) * alpha)) ** 3
	cdnc[(cdnc < 1)] = np.nan
	
	modis_dict = {'cwp': cwp, 'iwp': iwp, 'cth': cth, 'cod': cod, 'l_re': l_re, 'i_re': i_re, 'cf': cf, 'modis_aod': aod, 'ml_frac': ml_frac, 'ml_ice_frac': ml_ice_frac, 'ml_liq_frac': ml_liq_frac, 'd_ctoaer': dis_c_aer}
	
	return modis_latitudes, modis_longitudes, modis_dict
