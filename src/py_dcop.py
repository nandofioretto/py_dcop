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
    import networkx as nx
    data_path = '/Users/nando/Repos/DCOP/py_dcop/data/'

    g_gen = DCOPGenerator(seed=1234)
    dcop = DCOPInstance()

    graph = g_gen.random_graph(nnodes=20, p1=0.2)
    #graph = g_gen.regular_grid(nnodes=5)
    #graph = g_gen.scale_free(nnodes=20)
    print('graph - nodes: ', graph.number_of_nodes(), ' edges:', graph.number_of_edges())

    dcop.generate_from_graph(G=graph, dsize=5, max_clique_size=3, cost_range=(0, 10), p2=1.0)

    dsa = Dsa('dsa', dcop, {'max_iter': 100, 'type': 'C', 'p': 0.7})
    #maxsum = MaxSum('maxsum', dcop, {'max_iter': 100, 'damping': 0.7})
    ccg_maxsum_c = CCGCentralized('ccg-maxsum-c', dcop, {'max_iter': 10, 'damping': 0.9}, seed=1234)
    #ccg_dsa = CCGDsa('ccg-dsa', dcop, {'max_iter':10, 'type': 'C', 'p': 0.7}, seed=1234)
    #ccg_maxsum = CCGMaxSum('ccg-maxsum', dcop, {'max_iter': 10, 'damping': 0.7}, seed=1234)

    for i in range(10):
        dsa.run()               # 1131
        #maxsum.run()             # 1355
        ccg_maxsum_c.run()        # 1379
        #for v in dcop.variables.values(): v.setRandomAssignment()    # 371
        #ccg_dsa.run()            # 1381
        #ccg_maxsum.run()        # 1310 (damping = 0)



    #algorithm.stats.printSummary(anytime=True)
        # 545

    # dsa = 333 / 357
    # maxsum = 445
    # ccg-dsa = 421 (1000 -- but was improving...)
