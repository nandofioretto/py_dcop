from core.dcop_instance import DCOPInstance
from algorithms.dsa import Dsa
from algorithms.max_sum import MaxSum
from algorithms.ccg_maxsum import CCGMaxSum
from algorithms.ccg_centralized import CCGCentralized
from algorithms.ccg_dsa import CCGDsa
from algorithms.rand import Rand
from algorithms.lp_solver import LPSolver

from utils.stats_collector import StatsCollector
from core.dcop_generator import DCOPGenerator
from math import sqrt
import argparse
from tqdm import tqdm
import pandas as pd
import os

DATA_PATH = '/Users/nando/Repos/DCOP/py_dcop/data/'
NEXPERIMEMTS = 5

parser = argparse.ArgumentParser( prog='py-dcop', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--algorithm', dest='algorithm', #type=str,
                    #default='ccg-maxsum',
                    help='one of [dsa|maxsum|ccg-maxsum|ccg-maxsum-c|ccg-dsa|'
                                'dsa&ccg-maxsum|dsa&ccg-maxsum-c|dsa&ccg-dsa]')
parser.add_argument('--iterations', dest='iterations', type=int,
                    default=5000,
                    help='number of iterations')
parser.add_argument('--seed', dest='seed', type=int,
                    default=1234,
                    help='a seed number')
parser.add_argument('--nagents', dest='nagents', type=int,
                    default=100,
                    help='the number of agents')
parser.add_argument('--domsize', dest='domsize', type=int,
                    default=3,
                    help='the domain size')
parser.add_argument('--graph', dest='graph', type=str,
                    default='rand 0.2, 1.0',
                    help='one of [rand p1 p2| sf | grid]')
parser.add_argument('--fileout', dest='fileout', type=str,
                    help='path and file for outputs')
args = parser.parse_args()



if __name__ == '__main__':

    ## Parse arguments
    nagents = args.nagents
    domsize = args.domsize
    iterations = args.iterations
    seed = args.seed
    algname = args.algorithm
    fileout = args.fileout

    assert algname in ['dsa','maxsum','ccg-maxsum','ccg-maxsum-c','ccg-dsa', 'dsa&ccg-maxsum','dsa&ccg-maxsum-c','dsa&ccg-dsa', 'dsa&rand'], parser.print_help()
    graph_args = args.graph.split()
    graph = graph_args[0]
    assert graph in ['rand', 'sf', 'grid'], parser.print_help()


    ## Generate DCOP Instance
    g_gen = DCOPGenerator(seed=seed)
    dcop = DCOPInstance(seed=seed)

    p1, p2 = 0.5, 1.0
    if graph == 'rand':
        if len(graph_args) == 2:
            p1, p2 = float(graph_args[1]), 1.0
        elif  len(graph_args) == 3:
            p1, p2 = float(graph_args[1]), float(graph_args[2])
        graph = g_gen.random_graph(nnodes=nagents, p1=p1)
    elif graph == 'sf':
        graph = g_gen.scale_free(nnodes=nagents)
    elif graph == 'grid':
        graph = g_gen.regular_grid(nnodes=int(sqrt(nagents)))

    print('graph - nodes: ', graph.number_of_nodes(), ' edges:', graph.number_of_edges())
    dcop.generate_from_graph(G=graph, dsize=domsize, max_clique_size=3, cost_range=(0, 10), p2=p2)
    print('gen dcop')
    ## Run algorithms
    alg1, alg2 = None, None
    if algname == 'dsa':
        alg1 = Dsa('dsa', dcop, {'max_iter': iterations, 'type': 'C', 'p': 0.07}, seed=seed)
        n_rep = 1
    elif algname == 'maxsum':
        alg1 = MaxSum('maxsum', dcop, {'max_iter': iterations, 'damping': 0.7}, seed=seed)
        n_rep = 1
    elif algname == 'ccg-maxsum':
        alg1 = CCGMaxSum('ccg-maxsum', dcop, {'max_iter': iterations, 'damping': 0.7}, seed=seed)
        n_rep = 1
    elif algname == 'ccg-maxsum-c':
        alg1 = CCGCentralized('ccg-maxsum-c', dcop, {'max_iter': iterations, 'damping': 0.9}, seed=seed)
        n_rep = 1
    elif algname ==  'ccg-dsa':
        alg1 = CCGDsa('ccg-dsa', dcop, {'max_iter':iterations, 'type': 'C', 'p': 0.7}, seed=seed)
        n_rep = 1
    elif algname == 'dsa&ccg-maxsum':
        alg1 = Dsa('dsa', dcop, {'max_iter': 100, 'type': 'C', 'p': 0.7}, seed=seed)
        alg2 = CCGMaxSum('ccg-maxsum', dcop, {'max_iter': 100, 'damping': 0.7}, seed=seed)
        n_rep = int(iterations / 200)
    elif algname == 'dsa&ccg-maxsum-c':
        alg1 = Dsa('dsa', dcop, {'max_iter': 100, 'type': 'C', 'p': 0.7}, seed=seed)
        alg2 = CCGCentralized('ccg-maxsum-c', dcop, {'max_iter': 100, 'damping': 0.9}, seed=seed)
        n_rep = int(iterations / 200)
    elif algname == 'dsa&ccg-dsa':
        alg1 = Dsa('dsa', dcop, {'max_iter': 100, 'type': 'C', 'p': 0.7}, seed=seed)
        alg2 = CCGDsa('ccg-dsa', dcop, {'max_iter': 100, 'type': 'C', 'p': 0.7}, seed=seed)
        n_rep = int(iterations / 200)
    elif algname == 'dsa&rand':
        alg1 = Dsa('dsa', dcop, {'max_iter': 100, 'type': 'C', 'p': 0.7}, seed=seed)
        alg2 = Rand('rand', dcop, {'max_iter': 1}, seed=seed)
        n_rep = int(iterations / 200)


    for k in range(NEXPERIMEMTS):
        seed += 1
        alg1.reset(seed)
        if alg2: alg2.reset(seed)

        with tqdm(total=iterations) as pbar:
            last_iter, last_msg, last_time = 0, 0, 0

            for i in range(n_rep):
                alg1.run(interactive=False, pbar=pbar)
                if alg2 is not None:
                    alg2.run(interactive=False, pbar=pbar, chain=True)

        filename, extension = os.path.splitext(fileout)
        StatsCollector.getDataFrameSummary().to_csv(filename + str(k) + extension)