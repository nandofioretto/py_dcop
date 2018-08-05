import numpy as np
from core.variable import Variable
from core.constraint import Constraint
from core.agent_state import AgentState

class Agent:
    def __init__(self, name, variables=[], constraints=[], seed=1234):
        self.name = name
        self.variables = variables.copy()
        # the set of constraints involving variables of this agent in their scope
        self.constraints = constraints.copy()
        # the set of constraints controlled by this agent
        self.controlled_constraints = constraints.copy()
        self.prng = np.random.RandomState(seed)
        self.neighbors = []
        self.state = AgentState(name, self, seed)

    def addNeighbor(self, neighbor, con):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            self.state.addNeighborsVariables(neighbor)

            # Initialize controlled constraints: This agent controls the constraint f only if f has in its scope var x
            # this agent controls x and x is the variable with smallest index among all vars in the scope of f
            if con in self.controlled_constraints:
                v_agt = [v.name for v in self.variables]
                v_con = sorted([v.name for v in con.scope])
                if v_con[0] not in v_agt:
                    self.controlled_constraints.remove(con)

    def setRandomAssignment(self):
        '''Initializes values of all its variables to random values'''
        for v in self.variables:
            v.setRandomAssignment()

    def setStateAssignment(self):
        '''Sets the agent variable assignment equal to those in its state'''
        for var in self.variables:
            var.setAssignment(self.state.variables_assignments[var.name])

    def __str__(self):
        return 'agent: ' + str(self.name) + '\t controls:' \
               + str([var.name for var in self.variables]) \
               + ' constraints: ' + str([con.name for con in self.constraints]) \
               + ' controlled: ' + str([con.name for con in self.controlled_constraints])