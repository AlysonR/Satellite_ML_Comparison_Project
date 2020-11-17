import numpy as np
from pyhdf.SD import SD, SDC
import matplotlib.pyplot as plt

def get_data(filename):
	dataset = SD(filename, SDC.READ)
	lats = dataset.select('YDim').get()
	lons = dataset.select('XDim').get()
	cwp = dataset.select('Cloud_Water_Path_Liquid_Mean_Mean').get() * dataset.select('Cloud_Water_Path_Liquid_Mean_Mean').attributes()['scale_factor']
	iwp = dataset.select('Cloud_Water_Path_Ice_Mean_Mean').get() * dataset.select('Cloud_Water_Path_Ice_Mean_Mean').attributes()['scale_factor']
	cth = dataset.select('Cloud_Top_Height_Mean_Mean').get() * dataset.select('Cloud_Top_Height_Mean_Mean').attributes()['scale_factor']
	cod = dataset.select('Cloud_Optical_Thickness_Combined_Mean_Mean').get() * dataset.select('Cloud_Optical_Thickness_Combined_Mean_Mean').attributes()['scale_factor']
	lre = dataset.select('Cloud_Effective_Radius_Liquid_Mean_Mean').get() * dataset.select('Cloud_Effective_Radius_Liquid_Mean_Mean').attributes()['scale_factor']
	ire = dataset.select('Cloud_Effective_Radius_Ice_Mean_Mean').get() * dataset.select('Cloud_Effective_Radius_Ice_Mean_Mean').attributes()['scale_factor']
	cf =  dataset.select('Cloud_Fraction_Mean_Mean').get() * dataset.select('Cloud_Fraction_Mean_Mean').attributes()['scale_factor']

	aod = dataset.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean').get() * dataset.select('AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean').attributes()['scale_factor']
	
	return lats, lons, cwp, iwp, cth, cod, lre, ire, cf, aod
