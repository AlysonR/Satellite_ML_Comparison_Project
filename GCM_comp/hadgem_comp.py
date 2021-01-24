import numpy as np
import sys
import get_data



hadgem_dir = '/badc/cmip6/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-MM/historical/r1i1p1f3/'


aod550_dir = hadgem_dir + 'AERmon/od550aer/gn/files/d20191207/'
aod870_dir = hadgem_dir + 'AERmon/od870aer/gn/files/d20191207/'
aod440_dir = hadgem_dir + 'AERmon/od440aer/gn/files/d20191207/'

u_dir = hadgem_dir + 'Amon/ua/gn/files/d20191207/'
v_dir = hadgem_dir + 'Amon/va/gn/files/d20191207/'
airt_dir = hadgem_dir + 'Amon/ta/gn/files/d20191207/'
slp_dir = hadgem_dir + 'Amon/psl/gn/files/d20191207/'
rh_dir = hadgem_dir + 'Amon/hur/gn/files/d20191207/'
bl_dir = hadgem_dir + '6hrPlev/bldep/gn/files/d20200923/'
sst_dir = hadgem_dir + 'Omon/tos/gn/files/d20191207/'
spechum_dir = hadgem_dir + 'Amon/hus/gn/files/d20191207/'
cf_dir = hadgem_dir + 'Amon/clt/gn/files/d20191207/'
pbl_dir = hadgem_dir + '6hrPlev/bldep/gn/files/d20200923/'
surf_rh_dir = hadgem_dir + 'Amon/hurs/gn/files/d20191207/'
ts_dir = hadgem_dir + 'Amon/ts/gn/files/d20191207/'
ps_dir = hadgem_dir + 'Amon/ps/gn/files/d20191207/'
heights_dir = hadgem_dir + 'Amon/zg/gn/files/d20191207/'
#should compare against calipso to see how ML derived compares to calipso simulator

omega_dir = '/badc/cmip6/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-MM/historical/r3i1p1f3/Amon/wap/gn/files/d20200601/'
def get_hadgem():
	return_dict = get_data.get_data(pbl_dir, sst_dir, airt_dir, slp_dir, rh_dir, spechum_dir, omega_dir, u_dir, v_dir, cf_dir, ts_dir, ps_dir, heights_dir, aod550_dir, aod870_dir, aod440_dir)
	return return_dict
#hadgem_dict = get_hadgem()
#np.save('hadgem_data', hadgem_dict)


