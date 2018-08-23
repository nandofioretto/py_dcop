from core.dcop_instance import DCOPInstance
from algorithms.dsa import Dsa
from algorithms.max_sum import MaxSum
from algorithms.ccg_maxsum import CCGMaxSum
from algorithms.ccg_centralized import CCGCentralized
from algorithms.ccg_dsa import CCGDsa
from algorithms.lp_solver import LPSolver

from utils.stats_collector import StatsCollector
from core.dcop_generator import DCOPGenerator

if __name__ == '__main__':
    data_path = '/Users/nando/Repos/DCOP/py_dcop/data/'

    g_gen = DCOPGenerator(seed=1234)
    dcop = DCOPInstance()

    graph = g_gen.random_graph(nnodes=10, p1=0.6)
    #graph = g_gen.regular_grid(nnodes=5)
    #graph = g_gen.scale_free(nnodes=20)
    dcop.generate_from_graph(G=graph, dsize=5, max_clique_size=2, cost_range=(0, 10))

    algorithm = Dsa('dsa', dcop, {'max_iter':100, 'type': 'C', 'p': 0.01})
    #algorithm = MaxSum('maxsum', dcop, {'max_iter': 100, 'damping': 0.9})
    #algorithm  = CCGMaxSum('ccg-maxsum', dcop, {'max_iter': 100, 'damping': 0.9}, seed=1234)
    #algorithm  = CCGCentralized('ccg-maxsum-c', dcop, {'max_iter': 100, 'damping': 0.9}, seed=1234)
    #algorithm = CCGDsa('ccg-dsa', dcop, {'max_iter':100, 'type': 'C', 'p': 0.01})
    #algorithm = LPSolver('lp', dcop, {'max_iter':1, 'relax': True})
    algorithm.run()
    StatsCollector.printSummary(anytime=True)

        # 545