from algorithms.algorithm import Algorithm
import numpy as np

class Dsa(Algorithm):
    def __init__(self, name, dcop_instance, args={'max_iter':10, 'type': 'A', 'p': 0.7}, seed=1234):
        super(Dsa, self).__init__(name, dcop_instance, args)
        self.dsa_type = args['type']
        self.dsa_p    = args['p']

    def onStart(self, agt):
        # First Iteration: Set random assignment
        agt.setRandomAssignment()
        agt.state.copyAgtAssignmentToState()

    def onCurrentCycle(self, agt):
        # Send/Receive new value to/from neighbors (i.e., populate neighboring agent's state)
        for neighbor in agt.neighbors:
            agt.state.recvNeighborsValues(neighbor)
            self.num_messages_sent += 1

        # Compute local gain
        local_constraints = list(set([con for var in agt.variables for con in var.constraints]))
        curr_cost = np.sum([con.evaluate() for con in local_constraints])

        best_new_cost = np.inf
        best_assignment_it = 0
        while agt.state.nextAssignment():
            new_cost = np.sum([con.evaluate(agt.state.variables_assignments) for con in local_constraints])
            if new_cost < best_new_cost:
                best_assignment_it = (agt.state.assignment_it-1)
                best_new_cost = new_cost
        # restore the agent assignment into the agent state (in case we don't perform the update
        agt.state.copyAgtAssignmentToState()

        # We want to minimize so we want that new cost < currCost
        Delta = curr_cost - best_new_cost
        if Delta > 0 or (Delta == 0 and self.dsa_type == 'C'):
            # Select new values with probability p
            if self.prng.binomial(n=1, p=self.dsa_p):
                # performs the update both in the agent's state and in the agent variables
                agt.state.setAssignmentIt(best_assignment_it)
                agt.setStateAssignment()