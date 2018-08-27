import networkx as nx
import numpy as np

from algorithms.algorithm import Algorithm
from utils.ccg_utils import transform_dcop_instance_to_ccg, set_var_value


class CCGCentralized(Algorithm):

    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping':0}, ccg=None, seed=1234):
        super(CCGCentralized, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        if ccg is not None:
            self.ccg = ccg
        else:
            self.ccg = transform_dcop_instance_to_ccg(dcop_instance)
        self.msgs = {u: {v: np.asarray([0,0]) for v in self.ccg.neighbors(u)} for u in self.ccg.nodes()}
        self.root = min([aname for aname in dcop_instance.agents])
        self.variables = dcop_instance.variables.values()
        self.var_ccg_nodes = {vname : [(u, data['rank']) for u, data in self.ccg.nodes(data=True)
                                                         if ('variable' in data and data['variable'] == vname)]
                                for vname in dcop_instance.variables}

    def onStart(self, agt):
        #agt.setRandomAssignment()

        self.msgs = {u: {v: self.prng.randint(10, size=2)
                         for v in self.ccg.neighbors(u)} for u in self.ccg.nodes()}

        if agt.name is self.root:
            for var in self.variables:
                v_val = var.value
                # Set associated node to 0 and all others to 1
                vc = []
                for (u, r) in self.var_ccg_nodes[var.name]:
                    if v_val == 0 or v_val != 0 and r != v_val:
                        vc.append(u)
                set_var_value(var, vc, self.var_ccg_nodes[var.name], self.prng)

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
                m = np.asarray([weights[u] + sum_without_v[1],
                               min(sum_without_v[0], sum_without_v[1] + weights[u])])

                # Normalize values
                m -= np.min(m) # m -= np.mean(m)

                # Add noise to help stabilizing convergence
                m += self.prng.normal(scale=1, size=len(m))

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
        for u in ccg.nodes():
            sum_msgs = np.sum(self.msgs[t][u] for t in ccg.neighbors(u))
            if sum_msgs[0] > sum_msgs[1] + weights[u]:
                vertex_cover.append(u)

        for var in self.variables:
            set_var_value(var, vertex_cover, self.var_ccg_nodes[var.name], self.prng)

    def onTermination(self, agt):
        pass
