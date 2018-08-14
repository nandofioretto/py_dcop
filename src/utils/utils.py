import networkx as nx

def takeMin(cost, best_c, i=None, best_i=None):
    if cost < best_c:
        return cost, i
    else:
        return best_c, best_i

def takeMax(cost, best_c, i=None, best_i=None):
    if cost > best_c:
        return cost, i
    else:
        return best_c, best_i

def insertInTuple(_tuple, _pos, _val):
    _tuple_l = list(_tuple)
    _tuple_l[_pos] = _val
    return tuple(_tuple_l)

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
