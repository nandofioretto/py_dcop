import random
import itertools
import json
import networkx as nx
import sys, getopt
import dcop_instance as dcop

def generate(G : nx.Graph, dsize = 2, p2=1.0, cost_range=(0, 10), def_cost = 0, int_cost=True, outfile='') :
    assert (0.0 < p2 <= 1.0)
    agts = {}
    vars = {}
    doms = {'0': list(range(0, dsize))}
    cons = {}

    for i in range(0, len(G.nodes())):
        agts[str(i)] = None
        vars[str(i)] = {'dom': '0', 'agt': str(i)}

    cid = 0
    for e in G.edges():
        arity = len(e)
        cons[str(cid)] = {'arity': arity, 'def_cost': def_cost, 'scope': [str(x) for x in e], 'values': []}

        for assignments in itertools.product(*([[0, 1], ] * arity)):
            val = {'tuple': []}
            val['tuple'] = list(assignments)
            if int_cost:
                val['cost'] = random.randint(*cost_range)
            else:
                val['cost'] = random.uniform(*cost_range)
            cons[str(cid)]['values'].append(val)
        cid += 1

    return agts, vars, doms, cons

def main(argv):
    agts = 10
    max_arity = 2
    max_cost = 10
    out_file = ''
    name = ''
    def rise_exception():
        print('Input Error. Usage:\nmain.py -a -r -c -n -o <outputfile>')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "a:r:c:n:o:h",
                                   ["agts=", "max_arity=", "max_cost=", "name=", "ofile=", "help"])
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
        elif opt in ('-r', '--max_arity'):
            max_arity = int(arg)
        elif opt in ('-c', '--max_cost'):
            max_cost = int(arg)
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-o", "--ofile"):
            out_file = arg
    return agts, max_arity, max_cost, name, out_file

###############
from core.dcop_instance import *
from itertools import product, permutations
from functools import reduce
import operator

def create_dcop_instance(G: nx.Graph, dsize, max_clique_size=np.inf,
                         cost_range=(0,10), p2=1.0, def_cost=0, seed=1234):
    dcop = DCOPInstance()
    prng = np.random.RandomState(seed)

    # Generate Variables
    for n in G.nodes:
        vname = 'v_' + str(n)
        domain = list(range(dsize))
        dcop.variables[vname] = Variable(name=vname, domain=domain, type='decision')

    # Generate constraints - one for each clique
    cliques = list(nx.find_cliques(G))
    for i, c in enumerate(cliques):
        if len(c) > max_clique_size:
            print('Skipping constraints! Fix!')
            continue
        name = 'c_' + str(i)
        scope = ['v_' + str(ci) for ci in c]
        domains = [dcop.variables[vname].domain for vname in scope]
        all_tuples = product(*domains)
        n = reduce(operator.mul, map(len, domains), 1)
        costs = prng.randint(low=0, high=10, size=n)
        con_values = {T: costs[i] for i, T in enumerate(all_tuples)}
        dcop.constraints[name] = Constraint(name, scope=[dcop.variables[vid] for vid in scope], values=con_values)
        # add constriant to variables
        for vid in scope:
            dcop.variables[vid].addConstraint(dcop.constraints[name])

    # Generate Agents
    for n in G.nodes:
        name, vid = 'a_'+str(n), 'v_'+str(n)
        agt_constraints = []
        for c in dcop.variables[vid].constraints:
            if c not in agt_constraints:
                agt_constraints.append(c)
        dcop.agents[name] = Agent(name, variables=[dcop.variables[vid]], constraints=agt_constraints)
        dcop.variables[vid].setOwner(dcop.agents[name])

    # Connect neighbors:
    for con in dcop.constraints:
        clique = [var.controlled_by for var in dcop.constraints[con].scope]
        for ai, aj in permutations(clique, 2):
            ai.addNeighbor(aj, dcop.constraints[con])

###############

if __name__ == '__main__':
    nagts, maxarity, maxcost, name, outfile = main(sys.argv[1:])

    G = nx.grid_graph([nagts, nagts]).to_undirected()
    while not nx.is_connected(G):
        G = nx.grid_graph(nagts).to_undirected()

    # Normalize Graph
    Gn = nx.empty_graph(nagts)
    map_nodes = {}
    nid = 0
    for n in G.nodes():
        map_nodes[n] = nid
        nid += 1
    for e in G.edges():
        Gn.add_edge(map_nodes[e[0]], map_nodes[e[1]])

    agts, vars, doms, cons = generate(Gn, cost_range=(0,maxcost))

    print('Creating DCOP instance' + name, ' G nodes: ', len(Gn.nodes()), ' G edges:', len(Gn.edges()))

    dcop.create_json_instance(name, agts, vars, doms, cons, outfile+'.json')
