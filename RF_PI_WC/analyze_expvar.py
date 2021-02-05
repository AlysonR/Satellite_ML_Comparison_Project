import numpy as np
import sys
import grid_from_lat_lon
import matplotlib.pyplot as plt

warm_dict = np.load('PIAI_12.npy', allow_pickle = True, encoding = 'bytes').item()
model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']

models = list(warm_dict.keys())
areas = list(warm_dict[models[0]].keys())
explained_variances = {}
for model in models:
	explained_variances[model] = []
for model in models:
	for area in areas:
		explained_variances[model].append(np.nanmean(warm_dict[model][area][b'explained_variance']))


for i, model in enumerate(explained_variances.keys()):
	print(model)
	plt.hist(explained_variances[model], histtype = 'step', lw = 3., label = str(model)[2:-1], color = model_colors[i])
plt.legend(fontsize = 16)
plt.xticks(size = 14)
plt.yticks(size = 14)
plt.ylabel('Number Regions', size = 16)
plt.xlabel('Explained Variance', size = 16)
plt.show()
