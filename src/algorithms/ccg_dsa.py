import numpy as np
import networkx as nx

from algorithms.algorithm import Algorithm
from utils.ccg_utils import transform_dcop_instance_to_ccg, set_var_value

class CCGDsa(Algorithm):
    def __init__(self, name, dcop_instance, args={'max_iter':10, 'type': 'A', 'p': 0.7}, seed=1234):
        super(CCGDsa, self).__init__(name, dcop_instance, args)
        self.dsa_type = args['type']
        self.dsa_p    = args['p']

        self.ccg = transform_dcop_instance_to_ccg(dcop_instance)
        self.root = min([aname for aname in dcop_instance.agents])
        self.view = {u: 0 for u in self.ccg.nodes()}
        self.values = {u: 0 for u in self.ccg.nodes()}
        self.variables = dcop_instance.variables.values()


    def onStart(self, agt):
        # First Iteration: Set random assignment
        agt.setRandomAssignment()

        if agt.name is self.root:
            for u in self.ccg.nodes():
                self.values[u] = self.prng.randint(0, 1)

    def onCycleStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        if agt.name is not self.root:
            return

        def evaluate(u, val_u, ccg, u_view, weights):
            sum_cost = np.sum(u_view[v] * weights[v] for v in ccg.neighbors(u)) + val_u * weights[u]
            if val_u == 0 and any(u_view[v] == 0 for v in ccg.neighbors(u)):
                sum_cost += 1 * [u_view[v] for v in ccg.neighbors(u)].count(0)
            return sum_cost
            # if val_u == 0 and any(u_view[v] == 0 for v in ccg.neighbors(u)):
            #     return np.inf
            # else:
            #     return np.sum(self.view[v] * weights[v] for v in ccg.neighbors(u)) + val_u * weights[u]

        ccg = self.ccg
        weights = nx.get_node_attributes(ccg, 'weight')

        for u in ccg.nodes:
            # Receive values into view:
            for v in ccg.neighbors(u):
                self.view[v] = self.values[v]
                self.num_messages_sent += 1

            # Get best value:
            curr_cost = evaluate(u, self.values[u], ccg, self.view, weights)
            # Compute local gain
            best_new_cost = [evaluate(u, 0, ccg, self.view, weights),
                             evaluate(u, 1, ccg, self.view, weights)]
            best_assignment = np.argmin(best_new_cost)

            # We want to minimize so we want that new cost < currCost
            Delta = curr_cost - np.min(best_new_cost)
            if Delta > 0 or (Delta == 0 and self.dsa_type == 'C'):
                # Select new values with probability p
                if self.prng.binomial(n=1, p=self.dsa_p):
                    self.values[u] = best_assignment

    def onCycleEnd(self, agt):
        if agt.name != self.root:
            return

        ccg = self.ccg
        vertex_cover = [u for u in ccg.nodes if self.values[u] == 1]
        #print('L= ', len(vertex_cover))
        for var in self.variables:
            set_var_value(var, vertex_cover, ccg, self.prng)
