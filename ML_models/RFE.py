from sklearn.feature_selection import RFE
from sklearn.svm import SVR
import src
import numpy as np


tiles_dir = '/home/users/rosealyd/ML_sat_obs/cloudy_tiles/'
X, y = src.get_X_y(tiles_dir)

train_X, test_X, train_y, test_y = train_test_split(X, y, test_size = .2, random_state = 37)

