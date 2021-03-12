import numpy as np
import sys
import grid_from_lat_lon
import matplotlib.pyplot as plt

warm_dict = np.load('PIAI_96.npy', allow_pickle = True, encoding = 'bytes').item()
model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']

models = list(warm_dict.keys())
areas = list(warm_dict[models[0]].keys())
differences = {}
for model in models:
	differences[model] = []
for model in models:
	for area in areas:

		differences[model].append(np.nanmean(warm_dict[model][area][b'values']) * 100)

bins = np.linspace(-10, 27, 20)
for i, model in enumerate(differences.keys()):
	print(model)
	plt.hist(differences[model], bins = bins, histtype = 'step', lw = 3., label = str(model)[2:-1], color = model_colors[i])
plt.legend(fontsize = 16)
plt.xticks(size = 14)
plt.yticks(size = 14)
plt.ylabel('Number Regions', size = 16)
plt.xlabel('Change in CF', size = 16)
plt.show()
