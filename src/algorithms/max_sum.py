import numpy as np
import itertools
from algorithms.algorithm import Algorithm
from utils.utils import take_min

class MaxSum(Algorithm):
    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping': 0}, seed=1234):
        super(MaxSum, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        # A centralized version:
        self.msg_from_var_to_con = { vname: {} for vname in dcop_instance.variables }
        self.msg_from_con_to_var = { cname: {} for cname in dcop_instance.constraints }

    def onStart(self, agt):
        # Initialize messages
        for var in agt.variables:
            for con in var.constraints:
                self.msg_from_var_to_con[var.name][con.name] = np.zeros(len(var.domain))
        for con in agt.controlled_constraints:
            #table_size = np.prod([len(var.domain) for var in con.scope])
            for var in con.scope:
                self.msg_from_con_to_var[con.name][var.name] = np.zeros(len(var.domain))

        # First Iteration: Set random assignment
        agt.setRandomAssignment()
        agt.state.copyAgtAssignmentToState()

    def onCycleStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        # Send messages (variables to functions)
        for v in agt.variables:
            for con in v.constraints:
                self.sendMsgVarToCon(con)

        # Send messages (functions to variable)
        for c in agt.controlled_constraints:
            for var in c.scope:
                self.sendMsgConToVar(var)

    def onCycleEnd(self, agt):
        pass

    def onTermination(self, agt):
        # Assign Values
        pass


class VariableNode:
    def __init__(self, var):
        self.var = var


    def sendMsgVarToCon(self, con):
        '''
        The message sent from a variable-node x to a function-node F at iteration i contains,
        for each of the values d in the domain of x, the sum of costs for d that was received
        from all function neighbors apart from F at iteration i-1
        The size of the message x -> F : dom_x
        '''
        values = np.sum(self.msg_from_con_to_var[con.name][var.name] for con in var.constraints)
        # Exclude values coming from this constraint
        table_var_to_con = values - self.msg_from_con_to_var[con.name][var.name]
        # Normalize values
        #table_var_to_con -= np.min(table_var_to_con)
        table_var_to_con -= np.mean(table_var_to_con)
        # Add noise to help stabilizing convergence
        table_var_to_con += self.prng.normal(scale=1.0, size=len(table_var_to_con))
        # Send message to constraint
        # Todo: need To update the iteration! (otherwise it will invalidate this message)
        self.msg_from_var_to_con[var.name][con.name] = table_var_to_con


class FactorNode:
    def __init__(self, con):
        self.con = con
        self.projected_assignments = {}

        for var in con.scope:
            var_idx = con.scope.index(var)
            domains = [v.domain for v in con.scope if v != var]
            domains.insert(var_idx, [0])
            self.projected_assignments[var_idx] = itertools.product(*domains)


    def sendMsgConToVar(self, var):
        '''
        A message sent from a function-node F to a variable-node x in iteration i includes
        for each possible value d in the domain of x,
        the minimal cost of any combination of assignments to the variables involved in F
        apart from x and the assignment of value d to variable x.
        The size of the message F -> x : dom(x)
        '''
        var_idx = self.con.scope.index(var)
        table_con_to_var = np.zeors(len(var.domain))

        for i, d in enumerate(var.domain):
            min_cost = np.inf
            for combo in self.projected_assignments[var_idx]:
                combo[var_idx] = d
                min_cost, _ = take_min(self.con.evaluateTuple(combo), min_cost)
            table_con_to_var[i] = min_cost

        # Todo: need To update the iteration! (otherwise it will invalidate this message)
        self.msg_from_con_to_var[con.name][var.name] = table_con_to_var




def take_min(cost, i, best_c, best_i):
    if cost < best_c:
        return cost, i
    else:
        return best_c, best_i