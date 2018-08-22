import networkx as nx
import numpy as np
import sys, getopt
import dcop_instance as dcop
import itertools

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def create_scale_free_graph(n):
    """Create an undirected and connected scale free graph with n nodes"""
    _Gsf = nx.Graph(nx.scale_free_graph(n).to_undirected())
    while not nx.is_connected(_Gsf):
        _Gsf = nx.Graph(nx.scale_free_graph(n).to_undirected())

    # Copy edges in a new graph and remove [...]
    Gsf = _Gsf.copy()
    for u,v in _Gsf.edges():
        if u == v:
            Gsf.remove_edge(u, v)
    return Gsf

def construct_federated_graph(n, Gsf, seed=123):
    G = nx.Graph()
    G.add_nodes_from(list(range(n)))
    dic_G_reverse = {i: None for i in range(len(Gsf.nodes()))}

    np.random.seed(seed)
    nodes = np.asarray(Gsf.nodes())
    np.random.shuffle(nodes)

    for i, u in enumerate(nodes):
        if i < n:
            dic_G_reverse[u] = i
        else:
            # build probability vector with i proportional to where neighbors lie in:
            neigh_u = Gsf.neighbors(u)
            L = [dic_G_reverse[v] for v in neigh_u]
            x = np.asarray([L.count(i) + 1 for i in range(n)])
            elem = np.random.choice(G.nodes(), 1, p=softmax(x))[0]
            dic_G_reverse[u] = elem

    for _u in G.nodes():
        for _i in Gsf.neighbors(_u):
            _v = dic_G_reverse[_i]
            if not G.has_edge(_u, _v) and not G.has_edge(_v, _u) and _u != _v:
                G.add_edge(_u, _v)
    return G

def generate(G : nx.Graph, dsize = 2, cost_range=(0, 10), def_cost = 0, int_cost=True, outfile='') :
    agts = {}
    vars = {}
    doms = {'0': list(range(0, dsize))}
    cons = {}

    cost_s = np.random.random_integers(cost_range[0], cost_range[1], size=G.number_of_nodes())
    cost_b = np.random.random_integers(cost_range[0], cost_range[1], size=G.number_of_nodes())

    for i in range(0, len(G.nodes())):
        agts[str(i)] = None
        vars[str(i)] = {'dom': '0', 'agt': str(i)}

    cid = 0
    for e in G.edges():
        arity = len(e)
        cons[str(cid)] = {'arity': arity, 'def_cost': def_cost, 'scope': [str(x) for x in e], 'values': []}

        u, v = e[0], e[1]
        cons[str(cid)]['values'].append({'tuple': [0,0], 'cost': 0})
        cons[str(cid)]['values'].append({'tuple': [0,1], 'cost': 0})
        cons[str(cid)]['values'].append({'tuple': [1,0], 'cost': 0})
        cons[str(cid)]['values'].append({'tuple': [1,1], 'cost': cost_b[u] + cost_b[v]})
        cid += 1


    return agts, vars, doms, cons


def main(argv):
    agts = 10
    max_arity = 2
    max_cost = 10
    out_file = ''
    name = ''
    def rise_exception():
        print('Input Error. Usage:\nmain.py -a -m -c -n -o <outputfile>')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "a:m:c:n:o:h",
                                   ["agts=", "size_sf_net=", "max_cost=", "name=", "ofile=", "help"])
    except getopt.GetoptError:
        rise_exception()
    if len(opts) != 5:
        rise_exception()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('main.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ('-a', '--agts'):
            agts = int(arg)
        elif opt in ('-m', '--size_sf_net'):
            max_arity = int(arg)
        elif opt in ('-c', '--max_cost'):
            max_cost = int(arg)
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-o", "--ofile"):
            out_file = arg
    return agts, max_arity, max_cost, name, out_file



if __name__ == '__main__':
    nagts, num_nodes_sf, maxcost, name, outfile = main(sys.argv[1:])

    Gsf = create_scale_free_graph(num_nodes_sf)
    G = construct_federated_graph(nagts, Gsf)

    print('Nodes:', len(G.nodes()), ' Edges:', len(G.edges()), '/', (len(G.nodes()) * (len(G.nodes()) - 1)) / 2, ' :',
          len(G.edges()) / ((len(G.nodes()) * (len(G.nodes()) - 1)) / 2))
    assert nx.number_connected_components(G) == 1, 'number of connected components: ' \
                                                   + str(nx.number_connected_components(G))

    agts, vars, doms, cons = generate(G, cost_range=(0,maxcost))

    print('Creating DCOP instance' + name, ' G nodes: ', len(G.nodes()), ' G edges:', len(G.edges()))

    dcop.create_xml_instance(name, agts, vars, doms, cons, outfile+'.xml')
    dcop.create_wcsp_instance(name, agts, vars, doms, cons, outfile+'.wcsp')
    #dcop.create_json_instance(name, agts, vars, doms, cons, outfile+'.json')



