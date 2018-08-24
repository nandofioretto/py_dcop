from algorithms.algorithm import Algorithm
import numpy as np

class Rand(Algorithm):
    def __init__(self, name, dcop_instance, args={'max_iter': 1}, seed=1234):
        super(Rand, self).__init__(name, dcop_instance, args, seed)

    def onCurrentCycle(self, agt):
        agt.setRandomAssignment()
