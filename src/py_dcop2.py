from core.dcop_instance import DCOPInstance
from algorithms.dsa import Dsa
from algorithms.max_sum import MaxSum
from algorithms.ccg_maxsum import CCGMaxSum
from algorithms.ccg_centralized import CCGCentralized
from algorithms.ccg_dsa import CCGDsa
from algorithms.rand import Rand
from algorithms.lp_solver import LPSolver
from utils.ccg_utils import dcop_instance_to_dimacs, CCG_EXECUTABLE_PATH
from tempfile import NamedTemporaryFile

from utils.stats_collector import StatsCollector
from core.dcop_generator import DCOPGenerator
from math import sqrt
import argparse
from tqdm import tqdm
import pandas as pd
import os
from io import StringIO
from tempfile import NamedTemporaryFile
import subprocess
import sys
import re


DATA_PATH = '/Users/nando/Repos/DCOP/py_dcop/data/'
NEXPERIMEMTS = 5

parser = argparse.ArgumentParser( prog='py-dcop', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--algorithm', dest='algorithm', type=str,
                    default=None,
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
                    default=None,
                    help='one of [rand-sparse | rand-dense | sf | grid]')
parser.add_argument('--filein', dest='filein', type=str,
                    default=None,
                    help='path and file for outputs')
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
    filein = args.filein
    graph = args.graph

    ##########################
    ## Generate DCOP Instance
    ##########################
    if filein is None:
        assert graph in ['rand-sparse', 'rand-dense', 'sf', 'grid'], parser.print_help()

        g_gen = DCOPGenerator(seed=seed)
        dcop = DCOPInstance(seed=seed)

        p1, p2 = 0.5, 1.0
        if graph == 'rand-sparse':
            p1 = 0.2
            graph = g_gen.random_graph(nnodes=nagents, p1=p1)
        elif graph == 'rand-dense':
            p1 = 0.5
            graph = g_gen.random_graph(nnodes=nagents, p1=p1)
        elif graph == 'sf':
            graph = g_gen.scale_free(nnodes=nagents)
        elif graph == 'grid':
            graph = g_gen.regular_grid(nnodes=int(sqrt(nagents)))
        print('graph - nodes: ', graph.number_of_nodes(), ' edges:', graph.number_of_edges())
        dcop.generate_from_graph(G=graph, dsize=domsize, max_clique_size=3, cost_range=(0, 10), p2=p2)

        if algname is None:
            dcop.to_file(fileout)
            exit()
    else:
        dcop = DCOPInstance(seed=seed, filepath=filein)

    ##########################
    ## Run algorithms
    ##########################
    if algname is not None:
        assert algname in ['dsa','maxsum','ccg-maxsum','ccg-maxsum-c','ccg-dsa', 'dsa&ccg-maxsum','dsa&ccg-maxsum-c','dsa&ccg-dsa', 'dsa&rand', 'lp', 'ccg-maxsum+', 'ccg-maxsum+k'], parser.print_help()

        alg1, alg2 = None, None
        r = max(1, iterations / 50)
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
            alg1 = CCGCentralized('ccg-maxsum-c', dcop, {'max_iter': iterations, 'damping': 0.7}, seed=seed)
            n_rep = 1
        elif algname ==  'ccg-dsa':
            alg1 = CCGDsa('ccg-dsa', dcop, {'max_iter':iterations, 'type': 'C', 'p': 0.7}, seed=seed)
            n_rep = 1
        elif algname == 'dsa&ccg-maxsum':
            alg1 = Dsa('dsa', dcop, {'max_iter': r, 'type': 'C', 'p': 0.7}, seed=seed)
            alg2 = CCGMaxSum('ccg-maxsum', dcop, {'max_iter': r, 'damping': 0.7}, seed=seed)
            n_rep = int(iterations / 2*r)
        elif algname == 'dsa&ccg-maxsum-c':
            alg1 = Dsa('dsa', dcop, {'max_iter': r, 'type': 'C', 'p': 0.7}, seed=seed)
            alg2 = CCGCentralized('ccg-maxsum-c', dcop, {'max_iter': r, 'damping': 0.9}, seed=seed)
            n_rep = int(iterations / 2*r)
        elif algname == 'dsa&ccg-dsa':
            alg1 = Dsa('dsa', dcop, {'max_iter': r, 'type': 'C', 'p': 0.7}, seed=seed)
            alg2 = CCGDsa('ccg-dsa', dcop, {'max_iter': r, 'type': 'C', 'p': 0.7}, seed=seed)
            n_rep = int(iterations / 2*r)
        elif algname == 'dsa&rand':
            alg1 = Dsa('dsa', dcop, {'max_iter': r, 'type': 'C', 'p': 0.7}, seed=seed)
            alg2 = Rand('rand', dcop, {'max_iter': 1}, seed=seed)
            n_rep = int(iterations / 2*r)
        elif algname == 'lp':
            alg1 = LPSolver('rand', dcop, {'max_iter': 1, 'relax': True}, seed=seed)
            n_rep = 1
        elif algname == 'ccg-maxsum+' or algname == 'ccg-maxsum+k':
            ifile = dcop_instance_to_dimacs(dcop)
            # Call the CCG construction program. Change delete to False to view output files
            with NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as f:
                print(ifile.getvalue(), file=f, flush=True)
                # print("Running " + ' '.join([CCG_EXECUTABLE_PATH, '-k', '-mm', '-ctmp.out', f.name]), file=sys.stderr)
                if algname == 'ccg-maxsum+k':
                    ccg_output = subprocess.check_output([CCG_EXECUTABLE_PATH, '-mm', f.name], encoding='utf-8')
                else:
                    ccg_output = subprocess.check_output([CCG_EXECUTABLE_PATH, '-k', '-mm', f.name], encoding='utf-8')

                lines = ccg_output.splitlines()
                print_res = False
                i = 0
                while not lines[i].startswith('ccg-maxsum-results-start'): i += 1
                i+=1
                while not lines[i].startswith('ccg-maxsum-results-end'):
                    itr, cost, msgs, time = re.split(r'\t+', lines[i].rstrip('\t'))
                    StatsCollector.addIterStats(algname, int(itr), int(cost), int(msgs), float(time))
                    i += 1
            
            ##########################
            ## Statistics
            ##########################
            if fileout is not None:
                filename, extension = os.path.splitext(fileout)
                StatsCollector.getDataFrameSummary().to_csv(filename + '0' + extension)
            else:
                StatsCollector.printSummary()
        
            exit()

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

            ##########################
            ## Statistics
            ##########################
            if fileout is not None:
                filename, extension = os.path.splitext(fileout)
                StatsCollector.getDataFrameSummary().to_csv(filename + str(k) + extension)
            else:
                StatsCollector.printSummary()