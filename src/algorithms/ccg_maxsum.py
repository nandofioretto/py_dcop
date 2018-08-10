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
import numpy as np
import itertools
from algorithms.algorithm import Algorithm
from core.constraint import Constraint
from core.agent import Agent
import networkx as nx
from utils.utils import takeMin, insertInTuple

class CCGMaxSum(Algorithm):

    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping':0}, seed=1234):
        super(CCGMaxSum, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        self.CCG_graph = None

        self.msgs = {}

    def onStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        pass

    def onCurrentCycle(self, agt):
        pass

    def onCycleEnd(self, agt):
        pass

    def onTermination(self, agt):
        pass



def transform_constraint_to_ccg_gadget(con: Constraint) -> nx.Graph:
    """
    Transforms a constraint into the associated CCG gadget
    :param con: A constraint (~core.constraint.Constraint)
    :return: A networkx instance: G = (V, E)
    with V = the set of nodes. Each v \in V has the following attributes:
        - name = str (The name of the original (decision) variable). If the variable is auxiliary, then
            this field does not matter.
        - type = [dec_var | aux_var]
        - value:Boolean
        - weight:Float
        E = the set of edges. Each (u,v) \in E has the following attributes:
        - weight:Float
    """
    pass

def merge_mwvc_constraints(agt1: str, G1: nx.Graph, agt2: str, G2:  nx.Graph) -> (nx.Graph, nx.Graph):
    """
        Merge the weights associated to the nodes of type 'dec_var' that have the same 'name'.
        It assigns

    :param agt1: The name of agent 1
    :param G1: The gadget graph associated to agent 1
    :param agt2: The name of agent 2
    :param G2: The gadget graph associated to agent 2
    :return: The pairs of gadget (gadget1 and gadget2) associated to agents 1 and 2, reps.
     processed after the merging operation.
    """
    shared_dec_vars = [n for n in G1.nodes for m in G2.nodes
                          if n == m and G1.nodes[n]['type'] == 'dec_var']
    for u in shared_dec_vars:
        if agt1 <= agt2:
            G1.nodes[u]['weight'] += G2.nodes[u]['weight']
            for e in G2.edges(u):
                G1.add_edge(e[0], e[1], w=G2.get_edge_data(*e)['w'])
            G2.remove_node(u)
        else:
            G2.nodes[u]['weight'] += G1.nodes[u]['weight']
            for e in G1.edges(u):
                G2.add_edge(e[0], e[1], w=G1.get_edge_data(*e)['w'])
            G1.remove_node(u)

    return G1, G2
