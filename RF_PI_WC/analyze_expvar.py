import numpy as np
import sys
import grid_from_lat_lon
import matplotlib.pyplot as plt

warm_dict = np.load('PIAI_96.npy', allow_pickle = True, encoding = 'bytes').item()
model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']

models = list(warm_dict.keys())
models.pop(2)
areas = list(warm_dict[models[0]].keys())
explained_variances = {}
for model in models:
	explained_variances[model] = []
for model in models:
	for area in areas:
		explained_variances[model].append(np.nanmean(warm_dict[model][area][b'explained_variance']))


for i, model in zip([0, 1, 3], explained_variances.keys()):
	print(model)
	bins = np.linspace(.95, 1, 30)
	plt.hist(explained_variances[model], bins = bins, histtype = 'step', lw = 3., label = str(model)[2:-1], color = model_colors[i])
plt.legend(fontsize = 16)
plt.xticks(size = 14)
plt.yticks(size = 14)
plt.ylabel('Number Regions', size = 16)
plt.xlabel('Explained Variance', size = 16)
plt.savefig('zoom_exp_var.png', transparent = True)
