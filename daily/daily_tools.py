import numpy as np


def interp(data, start_lat, start_lon, end_lat, end_lon):
	from scipy import interpolate
	
	function = interpolate.interp2d(start_lon, start_lat, data, kind = 'linear')
	new_data = function(end_lon, end_lat)
	return new_data

