import numpy as np
from core.variable import Variable
from core.constraint import Constraint
from core.agent_state import AgentState

class Agent:
    def __init__(self, name, variables=[], constraints=[], seed=1234):
        self.name = name
        self.variables = variables
        self.constraints = constraints
        self.prng = np.random.RandomState(seed)
        self.neighbors = []
        self.state = AgentState(name, self, seed)

    def addNeighbor(self, neighbor):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            self.state.addNeighborsVariables(neighbor)

    def setRandomAssignment(self):
        '''Initializes values of all its variables to random values'''
        for v in self.variables:
            v.setRandomAssignment()

    def setStateAssignment(self):
        '''Sets the agent variable assignment equal to those in its state'''
        for var in self.variables:
            var.setAssignment(self.state.variables_assignments[var.name])

    def __str__(self):
        return 'agent: ' + str(self.name) + '\t controls:' + \
               str([var.name for var in self.variables]) \
               + ' constraints: ' + str([con.name for con in self.constraints])