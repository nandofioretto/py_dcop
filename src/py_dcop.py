from core.dcop_instance import DCOPInstance
from algorithms.dsa import Dsa
from algorithms.max_sum import MaxSum
from utils.stats_collector import StatsCollector

if __name__ == '__main__':
    #data_path = '/Users/nando/Repos/DCOP/py_dcop/data/'
    data_path = '/Users/ferdinandofioretto/Repos/py_dcop/data/'
    dcopIstance = DCOPInstance(data_path + 'binary.json')
    #algorithm = Dsa('dsa', dcopIstance, {'max_iter':10, 'type': 'A', 'p': 0.7})
    algorithm = MaxSum('maxsum', dcopIstance, {'max_iter': 10, 'damping': 0.0})
    algorithm.run()
    StatsCollector.printSummary()