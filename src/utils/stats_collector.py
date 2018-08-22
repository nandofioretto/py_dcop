iter_stats = []
import numpy as np
class StatsCollector:

    @staticmethod
    def updateIterStats(alg):
        iter_stats.append({'iteration': alg.curr_iteration,
                           'messages': alg.num_messages_sent,
                           'time': alg.curr_runtime,
                           'cost': alg.instance.cost()})
        print(iter_stats[-1]['cost'])

    @staticmethod
    def printSummary(anytime=True):
        print('iter\tmsgs\ttime\tcost')
        best_cost = np.inf
        for s in iter_stats:
            best_cost = min(s['cost'], best_cost)
            print(s['iteration'], s['messages'], round(s['time'], 4),
                  best_cost if anytime else s['cost'], sep='\t\t')