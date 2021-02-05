import numpy as np
import sys
import grid_from_lat_lon
import matplotlib.pyplot as plt

warm_dict = np.load('PIAI_12.npy', allow_pickle = True, encoding = 'bytes').item()
model_colors = ['#20ab2e', '#4042c7', '#bc87e8', '#ab2020']
#if train do train error otherwise test error
train_error = False
models = list(warm_dict.keys())
areas = list(warm_dict[models[0]].keys())
errors = {}
for model in models:
	errors[model] = []
for model in models:
	for area in areas:
		if train_error:
			errors[model].append(np.nanmean(warm_dict[model][area][b'train_error']) * 100)
		else:
			errors[model].append(np.nanmean(warm_dict[model][area][b'mses']) * 100)
if train_error:	
	bins = np.linspace(0, .36, 20)
else:
	bins = np.linspace(.17, 1.5, 20)
#for i, model in enumerate(errors.keys()):
for i, model in zip([0, 1, 3], [b'RF', b'SGB', b'XG']):
	print(model)
	plt.hist(errors[model], bins = bins, histtype = 'step', lw = 3., label = str(model)[2:-1], color = model_colors[i])
plt.legend(fontsize = 16)
plt.xticks(size = 14)
plt.yticks(size = 14)
plt.ylabel('Number Regions', size = 16)
if train_error:
	plt.xlabel('Train MSE (%CF)', size = 16)
else:
	plt.xlabel('Test MSE (%CF)', size = 16)
plt.show()
