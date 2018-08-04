'''Every agent has an agent state, which is its local view of the world'''
import numpy as np
import itertools

class AgentState:
    def __init__(self, name, agt, seed=1234):
        self.name = name
        self.prng = np.random.RandomState(seed)

        # contains the variable assignment (exploreD) for this agent and its neighbors
        self.variables_assignments = {var.name: var.value for var in agt.variables}

        self.this_agt = agt

        ## Data structures to explore assignment local to an agent
        self.my_vars = [var.name for var in agt.variables]
        # the iterator to all possible assignment for this agent
        self.assignment_it = 0
        # All possible assignments for the variables of this agent
        domains = [var.domain for var in agt.variables]
        self.agt_assignments_list = list(itertools.product(*domains))

    def addNeighborsVariables(self, neighbor):
        for var in neighbor.variables:
            self.variables_assignments[var.name] = var.value

    def recvNeighborsValues(self, neighbor):
        for var in neighbor.variables:
            self.variables_assignments[var.name] = var.value

    def copyAgtAssignmentToState(self):
        for var in self.this_agt.variables:
            self.variables_assignments[var.name] = var.value

    def nextAssignment(self):
        '''
        If a next assignment for the agent local variables exists, then assign it
        :var self.variables_assignments and return True. Otherwise return False.
        '''
        if self.assignment_it < len(self.agt_assignments_list):
            self.setAssignmentIt(self.assignment_it)
            self.assignment_it += 1
            return True
        else:
            # Reset iterator
            self.assignment_it = 0
            return False

    def setAssignmentIt(self, it):
        for i, var_name in enumerate(self.my_vars):
            self.variables_assignments[var_name] = self.agt_assignments_list[it][i]