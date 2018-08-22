from core.dcop_instance import DCOPInstance
from algorithms.dsa import Dsa
from algorithms.max_sum import MaxSum
from algorithms.ccg_maxsum import CCGMaxSum
from algorithms.ccg_centralized import CCGCentralized

from utils.stats_collector import StatsCollector
from core.dcop_generator import DCOPGenerator

if __name__ == '__main__':
    data_path = '/Users/nando/Repos/DCOP/py_dcop/data/'

    g_gen = DCOPGenerator()
    dcop = DCOPInstance()

    #graph = g_gen.regular_grid(nnodes=10)
    print('Generating Graph')
    graph = g_gen.random_graph(nnodes=20, p1=0.6)
    print('done')
    dcop.generate_from_graph(G=graph, dsize=5, cost_range=(0, 10))
    #dcopIstance = DCOPInstance(data_path + 'binary.json')

    #algorithm = Dsa('dsa', dcop, {'max_iter':100, 'type': 'C', 'p': 0.7})
    algorithm = MaxSum('maxsum', dcop, {'max_iter': 100, 'damping': 0.9})
    #algorithm  = CCGMaxSum('ccg-maxsum', dcop, {'max_iter': 100, 'damping': 0.9}, seed=1234)
    #algorithm  = CCGCentralized('ccg-maxsum', dcop, {'max_iter': 100, 'damping': 0.9}, seed=1234)
    algorithm.run()
    StatsCollector.printSummary(anytime=True)

    # 5486