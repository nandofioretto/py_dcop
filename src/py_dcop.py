from core.dcop_instance import DCOPInstance
from algorithms.dsa import Dsa
from algorithms.max_sum import MaxSum
from utils.stats_collector import StatsCollector

from algorithms.ccg_maxsum import transform_dcop_instance_to_ccg
if __name__ == '__main__':
    data_path = '/Users/nando/Repos/DCOP/py_dcop/data/'
    #data_path = '/Users/ferdinandofioretto/Repos/py_dcop/data/'
    dcopIstance = DCOPInstance(data_path + 'binary.json')
    print(dcopIstance)

    G = transform_dcop_instance_to_ccg(dcopIstance)
    print(G.nodes().data())
    print(G.edges().data())

    #algorithm = Dsa('dsa', dcopIstance, {'max_iter':10, 'type': 'A', 'p': 0.7})
    #algorithm = MaxSum('maxsum', dcopIstance, {'max_iter': 10, 'damping': 0.0})
    #algorithm.run()
    StatsCollector.printSummary()