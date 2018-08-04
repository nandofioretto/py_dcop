import os
import numpy as np
import itertools

cwd = os.getcwd()
root_path = os.path.dirname(os.path.realpath(cwd + '/../../'))
data_path = root_path + '/data/'

seed=1234
prng = np.random.RandomState(seed)

print(prng.binomial(n=1, p=0.1))

domains = [[0,1,2], [0,1,2], [0,1,2]]

all_tuples = list(itertools.product(*domains))

print (all_tuples)