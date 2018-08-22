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
from utils.ccg_utils import transform_dcop_instance_to_ccg, make_gadgets


class CCGMaxSum(Algorithm):
    # TODO: problem - agents need to hold copy of variables in the CCG which is actually controlled by other agents.
    # However in line 66 for v in ccg.nodes() - each agent uses all its nodes in its CCG to send messages. This should be fixed!
    # One solution is to return gadgets that are links to the nodes of the centralied CCG

    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping':0}, seed=1234):
        super(CCGMaxSum, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        self.ccg = transform_dcop_instance_to_ccg(dcop_instance)
        self.msgs = {u: {v: np.asarray([0,0]) for v in self.ccg.neighbors(u)} for u in self.ccg.nodes()}
        self.agt_ccg = make_gadgets(self.ccg, dcop_instance)
        self.agt_ccg_nodes = {}

    def onStart(self, agt):
        agt.setRandomAssignment()
        ccg = self.agt_ccg[agt.name]
        self.agt_ccg_nodes[agt.name] = [u for u, data in ccg.nodes(data=True)
                                        if 'owner' in data and data['owner'] == agt.name]


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
        for u in ccg.nodes:
            sum_msgs = np.sum(self.msgs[t][u] for t in ccg.neighbors(u))

            if sum_msgs[0] > sum_msgs[1] + weights[u]:
                vertex_cover.append(u)
            # if weights[u] < sum_msgs:
            #     vertex_cover.append(u)

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
        ccg = self.agt_ccg[var.controlled_by.name]

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
            N = len(node_rank_pairs)
            if N == 0:
                var.setAssignment(0)
            else:
                var.setAssignment(node_rank_pairs[-1])#self.prng.randint(0, N)])
