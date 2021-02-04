import numpy as np
import glob
import sys
import copy
import matplotlib.pyplot as plt

	
#from stackoverflow im not above "help"
def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
    
    assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))

#get_large_X_y(['EIS', 'sst'], 'cf', range(2003, 2004))
#get_N_X_y(['EIS', 'sst', 'tot_ang', 'tot_aod'], 'cf', 2008, 4)
#get_quad_X_y(['EIS', 'sst', 'tot_ang', 'tot_aod'], 'cf', 2007)
#get_single_X_y(['EIS', 'sst', 'tot_ang', 'tot_aod'], 'cf', 2007)

