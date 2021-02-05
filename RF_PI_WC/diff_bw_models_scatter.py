import numpy as np
import sys
import grid_from_lat_lon
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import cmap

brcmap = cmap.get_cmap()
warm_dict = np.load('PIAI_12.npy', allow_pickle = True, encoding = 'bytes').item()
model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']

models = list(warm_dict.keys())
model_names = ['Random Forest', 'SGB', 'MVLR', 'XGBoost']
regions = warm_dict[models[0]].keys()
areas = [str(b)[2:-1] for b in regions]

differences = {}
for model in models:
	differences[model] = []
for model in models:
	for area in regions:
		differences[model].append(np.nanmean(warm_dict[model][area][b'values']))


plt.plot([-1, 1], [-1, 1], '--', lw = 2.6, c = 'k')

plt.scatter(differences[b'RF'], differences[b'SGB'], c = model_colors[1], s = 100, label = 'SGB')
plt.scatter(differences[b'RF'], differences[b'XG'], c = model_colors[-1], s = 100, label = 'XGBoost')
plt.scatter(differences[b'RF'], differences[b'MVLR'], c = model_colors[2], s = 100, label = 'MVLR')

plt.xlim(-.055, .25)
plt.ylim(-.1, .25)
plt.xlabel('Random Forest Derived Change in Cloud Fraction', size = 18)
plt.ylabel('Other Model Derived Change in Cloud Fraction', size = 18)
plt.legend(fontsize = 15)

plt.xticks(size = 16)
plt.yticks(size = 16)
plt.show()
	
