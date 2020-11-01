"""
Provided by Norm Wood, 6/18/14

Examples of use:

Scalar variable
###############

import pyhdf.HDF
import CloudSat_tools.read_var

f_ptr = pyhdf.HDF.HDF(filename, pyhdf.HDF.HC.READ)
var = CloudSat_tools.read_var.get_0D_var(f_ptr, varname)


1D variable
###########

import pyhdf.HDF
import CloudSat_tools.read_var

f_ptr = pyhdf.HDF.HDF(filename, pyhdf.HDF.HC.READ)
var = CloudSat_tools.read_var.get_1D_var(f_ptr, varname)

2D variable
###########

import pyhdf.SD
import CloudSat_tools.read_var

f_ptr = pyhdf.SD.SD(filename, pyhdf.SD.SDC.READ)
var = CloudSat_tools.read_var.get_2D_var(f_ptr, varname)

"""

import numpy
import warnings

with warnings.catch_warnings():
   warnings.filterwarnings("ignore",category=DeprecationWarning)
   import pyhdf.HDF
   import pyhdf.VS
   import pyhdf.SD

def get_0D_var(file_VS_ptr, varname):
   vs = file_VS_ptr.vstart()
   var = vs.attach(varname)
   tmp = var.read(1)
   var_value = tmp[0][0]
   return(var_value)

def get_1D_var(file_VS_ptr, varname):
   vs = file_VS_ptr.vstart()
   var = vs.attach(varname)
   var_info = var.inquire()
   var_nRecs = var_info[0]
   tmp = var.read(var_nRecs)
   var_values = numpy.array(tmp)
   var.detach()
   return(var_values)
  
def get_1D_vars(file_VS_ptr):
	vs = file_VS_ptr.vstart()
	variables = []
	for var in vs.vdatainfo():
		variables.append(var[0])
	return variables

def get_2D_var(file_SD_ptr, varname, scale_default = None, offset_default = None):
   with warnings.catch_warnings():
      warnings.filterwarnings("ignore",category=DeprecationWarning)
      var = file_SD_ptr.select(varname)
      try:
         scale_factor = var.attributes()['factor']
      except KeyError:
         if scale_default != None:
            scale_factor = scale_default
         else:
            scale_factor = 1.
      try:
         offset = var.attributes()['offset']
      except KeyError:
         if offset_default != None:
            offset = offset_default
         else:
            offset = 0.
      var_values = (var[:]-offset)/scale_factor
      return var_values
