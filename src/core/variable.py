import numpy as np

class Variable:
    def __init__(self, name, domain=[], type='decision', seed=1234):
        self.name = name
        self.value = None
        self.type = type
        self.domain = domain.copy()
        self.constraints = []
        self.controlled_by = None
        self.prng = np.random.RandomState(seed)

    def init(self, domain, type='decision'):
        self.domain = domain
        self.type = type

    def addConstraint(self, constraint):
        if constraint.name not in [c.name for c in self.constraints]:
            self.constraints.append(constraint)

    def setOwner(self, agent):
        self.controlled_by = agent

    def setAssignment(self, value):
        self.value = value
        return value

    def setRandomAssignment(self):
        self.value = self.prng.choice(self.domain)
        return self.value

    def __str__(self):
        s = 'variable: ' + str(self.name) + '\t agt='
        if self.controlled_by is not None:
            s += '(' + str(self.controlled_by.name) + ') '
        else:
            s += '(TBD)'
        s += ' dom=' + str(self.domain)
        if self.value is not None:
            s += ' val=' + str(self.value)
        else:
            s += ' val=NA'
        return s