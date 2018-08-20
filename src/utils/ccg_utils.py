CCG_EXECUTABLE_PATH = '/Users/nando/Repos/DCOP/py_dcop/third_parties/wcsp/build/bin/wcsp'

from io import StringIO
from tempfile import NamedTemporaryFile
import subprocess
import sys
import networkx as nx
from core.dcop_instance import DCOPInstance

def load_dimacs_to_networkx(s):
    """Load a DIMACS graph file into a vertex-weighted networkx Graph.

    :param s: The input stream that hosts the DIMACS file.
    :return: A vertex-weighted networkx Graph.
    """
    g = nx.Graph()

    # First line: some graph metadata
    metadata = s.readline().split()
    nv = int(metadata[2])
    ne = int(metadata[3])

    # Add nodes
    for i in range(nv):
        _, node_id, node_weight = s.readline().strip().split()
        g.add_node(node_id, weight=float(node_weight))

    # Add edges
    for i in range(ne):
        _, node1, node2 = s.readline().strip().split()
        g.add_edge(node1, node2)

    return g

def transform_dcop_instance_to_ccg(instance: DCOPInstance) -> nx.Graph:
    """
    Transforms a DCOP instance into the associated CCG
    :param instance: A DCOP instance (~core.dcop_instance.DCOPInstance)
    :return: A networkx instance: G = (V, E)
    with V = the set of nodes. Each v \in V has the following attributes:
        - name = str (The name of the original (decision) variable). If the variable is auxiliary, then
            this field does not matter.
        - type = [decision | auxiliary]
        - value:Boolean
        - weight:Float
        E = the set of edges. Each (u,v) \in E has the following attributes:
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

# Not used
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


def make_gadgets(G, dcop_instance):

    def add_node_from(G_to, G_from, n):
        G_to.add_node(n)
        for attr in G_from.nodes[n]:
            G_to.nodes[n][attr] = G_from.nodes[n][attr]

    #G = transform_dcop_instance_to_ccg(dcop_instance)

    # Associates variables to CCG nodes
    var_to_ccg_nodes = {vname: [] for vname in dcop_instance.variables}
    for n, d in G.nodes(data=True):
        if 'variable' in d:
            var_to_ccg_nodes[d['variable']].append(n)


    G_agts = {aname: nx.Graph() for aname in dcop_instance.agents}

    ## Partition the nodes among agents:
    processed_nodes = []
    for v in dcop_instance.variables:
        a = dcop_instance.variables[v].controlled_by.name
        for n in var_to_ccg_nodes[v]:
            add_node_from(G_agts[a], G, n)
            processed_nodes.append(n)

        for n in var_to_ccg_nodes[v]:
            ngbs_n = G.neighbors(n)
            for m in ngbs_n:
                if m not in processed_nodes:
                    add_node_from(G_agts[a], G, m)
                    processed_nodes.append(m)

    assert (G.number_of_nodes() == len(processed_nodes))

    ## Partition edges among agents
    processed_edges = []
    for v in dcop_instance.variables:
        a = dcop_instance.variables[v].controlled_by.name
        tmp = []
        for n in G_agts[a].nodes:
            for e in nx.edges(G, n):
                if (e[0], e[1]) in processed_edges: continue
                if (e[1], e[0]) in processed_edges: continue
                processed_edges.append((e[0], e[1]))
                processed_edges.append((e[1], e[0]))
                tmp.append(e)
        G_agts[a].add_edges_from(tmp)
    # Check all edges have been assigned
    assert (G.number_of_edges() * 2 == len(processed_edges))

    for v in dcop_instance.variables:
        a = dcop_instance.variables[v].controlled_by.name
        for (n1, n2) in G_agts[a].edges:
            add_node_from(G_agts[a], G, n2)

    return G_agts
    