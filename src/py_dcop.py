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

    graph = g_gen.random_graph(nnodes=40, p1=0.2)
    print('graph - nodes: ', graph.number_of_nodes(), ' edges:', graph.number_of_edges())
    #graph = g_gen.regular_grid(nnodes=5)
    #graph = g_gen.scale_free(nnodes=20)
    dcop.generate_from_graph(G=graph, dsize=5, max_clique_size=2, cost_range=(0, 10))

    dsa = Dsa('dsa', dcop, {'max_iter': 10, 'type': 'C', 'p': 0.7})
    #maxsum = MaxSum('maxsum', dcop, {'max_iter': 10, 'damping': 0.7})
    #ccg_maxsum_c = CCGCentralized('ccg-maxsum-c', dcop, {'max_iter': 10, 'damping': 0.9}, seed=1234)
    #ccg_maxsum = CCGMaxSum('ccg-maxsum', dcop, {'max_iter': 10, 'damping': 0.7}, seed=1234)
    ccg_dsa = CCGDsa('ccg-dsa', dcop, {'max_iter':10, 'type': 'C', 'p': 0.7})

    for i in range(10):
        dsa.run()               # 394
        #maxsum.run()           # 393
        #ccg_maxsum_c.run()     # 381
        #for v in dcop.variables.values(): v.setRandomAssignment()    # 371
        #ccg_maxsum.run()       # 375 (damping = 0)
        ccg_dsa.run()          # 394



    #algorithm.stats.printSummary(anytime=True)
        # 545

    # dsa = 333 / 357
    # maxsum = 445
    # ccg-dsa = 421 (1000 -- but was improving...)
