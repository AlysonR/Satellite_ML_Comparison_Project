import numpy as np
import sys
import grid_from_lat_lon
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import cmap
from pylab import rcParams
rcParams['figure.figsize'] = 13, 6


brcmap = cmap.get_cmap()
warm_dict = np.load('PIAI_96.npy', allow_pickle = True, encoding = 'bytes').item()
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


for i, model in enumerate(differences.keys()):
	points = [x for _, x in sorted(zip(differences[b'RF'], differences[model]))]
	plt.plot(range(len(differences[model])), points, c = model_colors[i], lw = 2, label = str(model)[2:-1])
	
	
plt.xlabel('Regions Sorted by Similarity', size = 20)
plt.ylabel('ML Derived Change in \n Warm Cloud Fraction', size = 20)
plt.legend(fontsize = 17)

plt.xticks([])
plt.yticks(size = 18)
plt.show()
	
