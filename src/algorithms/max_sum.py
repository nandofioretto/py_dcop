import numpy as np
import itertools
from algorithms.algorithm import Algorithm
from utils.utils import takeMin, insertInTuple

class MaxSum(Algorithm):
    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping': 0}, seed=1234):
        super(MaxSum, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        self.msg_from_var_to_con = { vname: {} for vname in dcop_instance.variables }
        self.msg_from_con_to_var = { cname: {} for cname in dcop_instance.constraints }

        self.vnodes = {vname: MaxSum.VariableNode(dcop_instance.variables[vname]) for vname in dcop_instance.variables}
        self.fnodes = {cname: MaxSum.FactorNode(dcop_instance.constraints[cname]) for cname in dcop_instance.constraints}

    def onStart(self, agt):
        # Initialize messages
        for var in agt.variables:
            for con in var.constraints:
                self.msg_from_var_to_con[var.name][con.name] = np.zeros(len(var.domain))

        for con in agt.controlled_constraints:
            for var in con.scope:
                self.msg_from_con_to_var[con.name][var.name] = np.zeros(len(var.domain))

        # First Iteration: Set random assignment
        agt.setRandomAssignment()
        agt.state.copyAgtAssignmentToState()

    def onCycleStart(self, agt):
        # Copy new messages into old messages
        pass

    def onCurrentCycle(self, agt):
        # Send messages (variables to functions)
        for v in agt.variables:
            for con in v.constraints:
                self.vnodes[v.name].sendMsgVarToCon(con, self)

        # Send messages (functions to variable)
        for c in agt.controlled_constraints:
            for var in c.scope:
                self.fnodes[c.name].sendMsgConToVar(var, self)

    def onCycleEnd(self, agt):
        # Select best value from all the variables controlled by this agent:
        for v in agt.variables:
            best_d_idx = np.argmin(np.sum(self.msg_from_con_to_var[c.name][v.name] for c in v.constraints))
            v.setAssignment(v.domain[best_d_idx])

    def onTermination(self, agt):
        pass


    class VariableNode:
        def __init__(self, var):
            self.var = var

        def sendMsgVarToCon(self, con, Mailer):
            """
            The message sent from a variable-node x to a function-node F at iteration i contains,
            for each of the values d in the domain of x, the sum of costs for d that was received
            from all function neighbors apart from F at iteration i-1
            The size of the message x -> F : dom_x
            :param con:
            :param Mailer:
            :return:
            """
            values = np.sum(Mailer.msg_from_con_to_var[con.name][self.var.name] for con in self.var.constraints)
            # Exclude values coming from this constraint
            table_var_to_con = values - Mailer.msg_from_con_to_var[con.name][self.var.name]
            # Normalize values
            table_var_to_con -= np.min(table_var_to_con)
            #table_var_to_con -= np.mean(table_var_to_con)
            # Add noise to help stabilizing convergence
            table_var_to_con += np.abs(Mailer.prng.normal(scale=1.0, size=len(table_var_to_con)))
            # Send message to constraint
            Mailer.num_messages_sent += 1
            if Mailer.damping > 0:
                table_var_to_con = Mailer.damping * Mailer.msg_from_var_to_con[self.var.name][con.name] \
                                   + (1-Mailer.damping) * table_var_to_con

            Mailer.msg_from_var_to_con[self.var.name][con.name] = table_var_to_con


    class FactorNode:
        def __init__(self, con):
            self.con = con

            self.projected_assignments = {}
            for var in con.scope:
                var_idx = con.scope.index(var)
                domains = [v.domain for v in con.scope if v != var]
                domains.insert(var_idx, [0])
                self.projected_assignments[var_idx] = itertools.product(*domains)


        def sendMsgConToVar(self, var, Mailer):
            '''
            A message sent from a function-node F to a variable-node x in iteration i includes
            for each possible value d in the domain of x,
            the minimal cost of any combination of assignments to the variables involved in F
            apart from x and the assignment of value d to variable x.
            The size of the message F -> x : dom(x)
            '''
            var_idx = self.con.scope.index(var)

            #############
            domains = [v.domain for v in self.con.scope if v != var]
            domains.insert(var_idx, [0])
            #############

            table_con_to_var = np.zeros(len(var.domain))

            for i, d in enumerate(var.domain):
                min_cost = np.inf
                for combo in itertools.product(*domains): #self.projected_assignments[var_idx]:
                    combo_d = insertInTuple(combo, var_idx, d)
                    min_cost, _ = takeMin(self.con.evaluateTuple(combo_d), min_cost)
                table_con_to_var[i] = min_cost

            # Todo: need To update the iteration! (otherwise it will invalidate this message)
            Mailer.num_messages_sent += 1
            Mailer.msg_from_con_to_var[self.con.name][var.name] = table_con_to_var
