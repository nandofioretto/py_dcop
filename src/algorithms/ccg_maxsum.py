"""
Schema:
    1. Each agent will hold a CCG graph: (X, Y, Z, E, w)
        - For each function of the DCOP f:
            transform_constraint_ccg_gadget(f) -> (X, V, Z, E, w)::G_i
            transform_ccg_gadget_to_mwvc_constraint(G_i) -> [c_1..c_k]
            merge_mwvc_constraints([]) -> [] # Also establishes ownership

    2. Solve Phase:
        - Each variable passes messages to their neighbors
        - msg_u->v(i) = max {0, w_u - \sum_{t \in N(u) \ {v}}  msg_t->u(i-1)}}

    3. Retrieve solution phase:
        - If w_v < \sum_{u \in N(v)} msg_u->v ==> v = 1 else v = 0
        - Take all decision variables controlled by an agent and get the value in
          original domain:
          map_mwvc_var_values_to_dcop_val( {vars : values} ) -> value

    TODO: Make this improvment: Since we are solving a MWVC - solve it optimally in each agent, and use the message
          passig algorithm only to exchange values among neighboring agents
"""
from io import StringIO
from operator import mul
from tempfile import NamedTemporaryFile
import itertools
import subprocess
import sys

import networkx as nx
import numpy as np

from algorithms.algorithm import Algorithm
from core.agent import Agent
from core.constraint import Constraint
from core.dcop_instance import DCOPInstance
from utils.utils import takeMin, insertInTuple
from utils.ccg_utils import transform_dcop_instance_to_ccg, make_gadgets, set_var_value


class CCGMaxSum(Algorithm):
    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping':0}, ccg=None, seed=1234):
        super(CCGMaxSum, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        if ccg is not None:
            self.ccg = ccg
        else:
            self.ccg = transform_dcop_instance_to_ccg(dcop_instance)
        self.msgs = {u: {v: np.asarray([0,0]) for v in self.ccg.neighbors(u)} for u in self.ccg.nodes()}
        self.agt_ccg = make_gadgets(self.ccg, dcop_instance)
        self.agt_ccg_nodes = {}

        self.var_ccg_nodes = {vname : [(u, data['rank']) for u, data in self.ccg.nodes(data=True)
                                                         if ('variable' in data and data['variable'] == vname)]
                                for vname in dcop_instance.variables}


    def onStart(self, agt):
        #agt.setRandomAssignment()
        ccg = self.agt_ccg[agt.name]
        self.agt_ccg_nodes[agt.name] = [u for u, data in ccg.nodes(data=True)
                                        if 'owner' in data and data['owner'] == agt.name]

        for var in agt.variables:
            v_val = var.value
            vc = []
            # Set associated node to 0 and all others to 1
            for (u, r) in self.var_ccg_nodes[var.name]:
                if v_val == 0 or v_val != 0 and r != v_val:
                    vc.append(u)
            set_var_value(var, vc, self.var_ccg_nodes[var.name], self.prng)

    def onCycleStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        ccg = self.agt_ccg[agt.name]
        weights = nx.get_node_attributes(ccg, 'weight')

        for u in self.agt_ccg_nodes[agt.name]:
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
        ccg = self.agt_ccg[agt.name]
        weights = nx.get_node_attributes(ccg, 'weight')
        type = nx.get_node_attributes(ccg, 'type')

        vertex_cover = []
        for u in ccg.nodes():
            sum_msgs = np.sum(self.msgs[t][u] for t in ccg.neighbors(u))

            if sum_msgs[0] > sum_msgs[1] + weights[u]:
                vertex_cover.append(u)
            # if weights[u] < sum_msgs:
            #     vertex_cover.append(u)

        for var in agt.variables:
            set_var_value(var, vertex_cover, self.var_ccg_nodes[var.name], self.prng)

    def onTermination(self, agt):
        pass
