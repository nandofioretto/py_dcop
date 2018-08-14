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
from utils.utils import takeMin, insertInTuple, load_dimacs_to_networkx


CCG_EXECUTABLE_PATH = 'wcsp'

class CCGMaxSum(Algorithm):

    def __init__(self, name, dcop_instance, args={'max_iter':10, 'damping':0}, seed=1234):
        super(CCGMaxSum, self).__init__(name, dcop_instance, args, seed)
        self.damping = args['damping']

        # If this were defined as a centralied import, then we can use the following code:
        self.ccg = importGGCGraph(args['ccg_graph'])
        self.msgs = {u: {v for v in self.ccg.neighbors(u)} for u in self.ccg.nodes()}
        self.agt_ccg = {aname: nx.Graph() for a in dcop_instance.agents}

    def onStart(self, agt):
        ccg = self.agt_ccg[agt]
        for u in ccg.nodes():
            for v in ccg.neighbors(u):
                self.msgs[u][v] = np.asarray([0, 0])

    def onCycleStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        ccg = self.agt_ccg[agt]
        weights = nx.get_node_attributes(ccg, 'weight')

        for u in ccg.nodes():
            # sum all messages from u's neighbors to itself
            sum_msgs = np.sum(self.msgs[t][u] for t in ccg.neighbors(u))

            # Send messages to neighbors
            for v in ccg.neighbors(u):
                sum_without_v = sum_msgs - self.msgs[t][u]
                m  = np.asarray([weights[u] + sum_without_v[1],
                                 np.min(sum_without_v[0], sum_without_v[1] + weights[u])])
                # Normalize values
                m -= np.min(m) # m -= np.mean(m)
                # Add noise to help stabilizing convergence
                m += np.abs(self.prng.normal(scale=1.0, size=len(m)))
                if self.damping > 0:
                    m = self.damping * self.msgs[u][v] + (1-self.damping) * m

                self.num_messages_sent += 1
                self.msgs[u][v] = m

    def onCycleEnd(self, agt):
        ccg = self.agt_ccg[agt]
        weights = nx.get_node_attributes(ccg, 'weight')
        type = nx.get_node_attributes(ccg, 'type')

        for var in agt.variables:
            u = var.name
            sum_msgs = np.sum(self.msgs[t][u] for t in ccg.neighbors(u))
            if weights[u] < sum_msgs:
                var.setAssignment(1)
            else:
                var.setAssignment(0)

    def onTermination(self, agt):
        pass

    def getVarValue(var):
        ccg = self.agt_ccg[var.controlled_by.name]
        weights = nx.get_node_attributes(ccg, 'weight')
        for u in ccg.neighbors(var.name):
            # .... Implement logic here

        pass

def importGGCGraph(file):
    pass


def transform_dcop_instance_to_ccg(instance: DCOPInstance) -> nx.Graph:
    """
    Transforms a DCOP instance into the associated CCG
    :param instance: A DCOP instance (~core.dcop_instance.DCOPInstance)
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
    # Each variable needs an ID
    variable_ids = dict()
    for i, (_, v) in enumerate(instance.variables.items()):
        variable_ids[v.name] = str(i)

    # Write input file for the CCG construction program
    max_domain_size = max(len(v.domain) for _, v in instance.variables.items())
    input_file = StringIO()
    print('edges {} {} {} 9999999'.format(
        len(instance.variables), max_domain_size, len(instance.constraints)),
          file=input_file)
    for _, v in instance.variables.items():
        print(len(v.domain), end=' ', file=input_file)
    print('', file=input_file)

    for _, c in instance.constraints.items():
        # constraint signature
        print(len(c.scope), end=' ', file=input_file)
        for v in c.scope:
            print(variable_ids[v.name], end=' ', file=input_file)
        print(c.default_value, end=' ', file=input_file)
        print(len(c.values), file=input_file)

        # tuples in the constraint
        for vs, w in c.values.items():
            print(' '.join(str(v) for v in vs) + ' ' + str(w), file=input_file)

    # Call the CCG construction program. Change delete to False to view output files
    with NamedTemporaryFile(mode='w+', encoding='utf-8', delete=True) as f:
        print(input_file.getvalue(), file=f, flush=True)
        print("Running " + ' '.join([CCG_EXECUTABLE_PATH, '-k', '-g', f.name]), file=sys.stderr)
        ccg_output = subprocess.check_output([CCG_EXECUTABLE_PATH, '-k', '-g', f.name],
                                             encoding='utf-8')

    # Construct CCG
    lines = ccg_output.splitlines()

    # Find the CCG part
    ccg_begin_index = None
    for i, line in enumerate(lines):
        if ccg_begin_index is None and line.startswith('p edges'):
            ccg_begin_index = i
        elif ccg_begin_index is not None and line.startswith('---'):
            ccg_end_index = i
            break

    # Load the CCG
    ccg = load_dimacs_to_networkx(StringIO('\n'.join(lines[ccg_begin_index:ccg_end_index])))
    nx.set_node_attributes(ccg, 'auxiliary', 'type')

    # Load mapping from non-Boolean variables to Boolean variables
    non_boolean_mapping_has_begun = False
    non_boolean_mapping = dict()  # from non Boolean variable to Boolean variables
    for line in lines:
        if 'Non-Boolean Variable Mapping BEGINS' in line:
            non_boolean_mapping_has_begun = True
            continue
        if non_boolean_mapping_has_begun:
            if 'Non-Boolean Variable Mapping ENDS' in line:
                break

            # Actual contents of mapping
            vs = line.split()
            non_boolean_mapping[vs[0]] = list(vs[1:])

    # Load mapping from Boolean variables to vertex
    boolean_mapping_has_begun = False
    boolean_mapping = dict()
    for line in lines:
        if 'vertex types begin' in line:
            boolean_mapping_has_begun = True
            continue
        if boolean_mapping_has_begun:
            if 'vertex types end' in line:
                break
            # Actual contents of mapping
            ver, bv = line.split()
            if int(bv) >= 0:  # dec_var
                boolean_mapping[bv] = ver

    # Set vertex attributes correctly
    for nbv, nbv_id in variable_ids.items():
        bvs = non_boolean_mapping[nbv_id]
        for i, bv in enumerate(bvs):
            ver = boolean_mapping[bv]
            ccg.nodes[ver]['type'] = 'decision'
            ccg.nodes[ver]['variable'] = nbv
            if len(bvs) == 1:
                ccg.nodes[ver]['rank'] = 0
            else:
                ccg.nodes[ver]['rank'] = i + 1

    return ccg

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


# from src.core.agent_state import AgentState
#
# class GGCAgentState(AgentState):
#     def __init__(self, name, agt, seed=1234):
#         super(GGCAgentState, self).__init__(name, agt, seed)
