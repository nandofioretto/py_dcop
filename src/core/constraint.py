import numpy as np
from core.variable import Variable

class Constraint:
    def __init__(self, name, scope=[], values={}, default_value = 0, type='extensional', seed=1234):
        self.name = name
        self.scope = scope.copy()
        self.type = type
        self.values = values.copy()
        self.default_value = default_value
        self.prng = np.random.RandomState(seed)

    def init(self, scope: list, values: dict, default_value = 0, type='extensional'):
        self.scope = scope
        self.values = values
        self.type = type
        self.default_value = default_value

    def evaluate(self, var_vals=None):
        '''takes in input a tuple of values of the type:
           { varid : value ... }
        '''
        if var_vals is None:
            return self.evaluateCurrentAssignment()

        # order the var_vals in the same order of scope
        eval_tuple = tuple([var_vals[var.name] for var in self.scope])
        return self.evaluateTuple(eval_tuple)

    def evaluateTuple(self, eval_tuple):
        '''Evaluates a tuple of values already ordreded as expected'''
        if eval_tuple in self.values:
            return self.values[eval_tuple]
        else:
            return self.default_value


    def evaluateCurrentAssignment(self):
        '''evaluate constraint with current variable assignment'''
        eval_tuple = tuple([var.value for var in self.scope])
        return self.values[eval_tuple] if eval_tuple in self.values else self.default_value

    def __str__(self):
        s = 'constraint: ' + str(self.name) + '\t'
        s += ' scope: ' + str([v.name for v in self.scope])
        s += ' values: ' + str(list(self.values.values()))
        return s
