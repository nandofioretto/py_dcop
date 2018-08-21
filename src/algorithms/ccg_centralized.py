import networkx as nx
import numpy as np

from algorithms.algorithm import Algorithm
from utils.ccg_utils import transform_dcop_instance_to_ccg, make_gadgets


class CCGCentralized(Algorithm):

    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping':0}, seed=1234):
        super(CCGCentralized, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        self.ccg = transform_dcop_instance_to_ccg(dcop_instance)
        self.msgs = {u: {v: np.asarray([0,0]) for v in self.ccg.neighbors(u)} for u in self.ccg.nodes()}
        self.root = min([aname for aname in dcop_instance.agents])

    def onStart(self, agt):
        agt.setRandomAssignment()

    def onCycleStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        if agt.name != self.root:
            return

        ccg = self.ccg
        weights = nx.get_node_attributes(ccg, 'weight')

        for u in ccg.nodes():
            # sum all messages from u's neighbors to itself
            sum_msgs = np.sum(self.msgs[t][u] for t in ccg.neighbors(u))

            # Send messages to neighbors
            for v in ccg.neighbors(u):
                sum_without_v = sum_msgs - self.msgs[v][u]
                m  = np.asarray([weights[u] + sum_without_v[1],
                                 min(sum_without_v[0], sum_without_v[1] + weights[u])])

                # Normalize values
                m -= np.min(m) # m -= np.mean(m)

                # Add noise to help stabilizing convergence
                m += self.prng.normal(scale=0.01, size=len(m))

                # Damping
                if self.damping > 0:
                    m = self.damping * self.msgs[u][v] + (1-self.damping) * m

                self.num_messages_sent += 1
                self.msgs[u][v] = m

    def onCycleEnd(self, agt):
        if agt.name != self.root:
            return

        ccg = self.ccg
        weights = nx.get_node_attributes(ccg, 'weight')
        vertex_cover = []
        for u in ccg.nodes:
            sum_msgs = np.sum(self.msgs[t][u] for t in ccg.neighbors(u))
            if sum_msgs[0] > sum_msgs[1] + weights[u]:
                vertex_cover.append(u)

        for var in agt.variables:
            self.setVarValue(var, vertex_cover)

    def onTermination(self, agt):
        pass

    def setVarValue(self, var, vc):
        """
        Get the value of a variable.
        :param var: The variable of interest.
        :param vc: The computed vertex cover, which is a set of nodes.
        """
        ccg = self.ccg

        if len(var.domain) == 2:  # Boolean variable
            for u, data in ccg.nodes(data=True):
                if 'variable' in data and data['variable'] == var.name:
                    assert(data['rank'] == 0)
                    var.setAssignment(1 if u in vc else 0)
        else:  # Non-Boolean variable
            # Get all nodes relevant to the variable of interest. We shouldn't need to find all such
            # pairs, but this would be easier for debugging.
            node_rank_pairs = tuple(
                data['rank'] for u, data in ccg.nodes(data=True)
                          if ('variable' in data and data['variable'] == var.name and u not in vc))
            #assert(len(node_rank_pairs) <= 1)
            if len(node_rank_pairs) == 0:
                var.setAssignment(0)
            else:
                var.setAssignment(node_rank_pairs[0])