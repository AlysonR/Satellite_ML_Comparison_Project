import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)
       
    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

def get_cmap():    
	cdict3 = {'red':  ((0.0, 0.0, 0.0),
                   (0.5, 1.0, 1.0),
                   (1.0, 1.0, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.5, 1.0, 1.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 1.0, 1.0),
                   (0.5, 1.0, 1.0),
                   (1.0, 0.0, 0.0))
        }
	plt.register_cmap(name = 'BlueRed', data = cdict3)
	cmap = plt.get_cmap('BlueRed')
	return cmap
	
def get_redmap():
	cdict4 = {'red': ((0.0, 1.0, 1.0),
					(.5, 1., 1.),
					(1., 1., 1.)),
			'green': ((0.0, 1.0, 1.0),
					(.5, .5, .5),
					(1.0, 0.0, 0.0)),
			'blue': ((0.0, 1.0, 1.0),
					(.5, .5, .5),
					(1.0, 0.0, 0.0))
			
			}

	plt.register_cmap(name = 'TrueRed', data = cdict4)
	cmap = plt.get_cmap('TrueRed')
	return cmap
	
def get_bluemap():
	cdict5  = {'blue': ((0.0, 1., 1.),
					(.5, 1., 1.),
					(1.0, 1.0, 1.0)),
			'green': ((0.0, 0.0, 0.0),
					(.5, .5, .5),
					(1.0, 1.0, 1.0)),
			'red': ((0.0, 0.0, 0.0),
					(.5, .5, .5),
					(1.0, 1.0, 1.0))
			
			}
	plt.register_cmap(name = 'TrueBlue', data = cdict5)
	cmap = plt.get_cmap('TrueBlue')
	return cmap
	
	
			
			
			
			
			
			

