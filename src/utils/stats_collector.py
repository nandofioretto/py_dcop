import numpy as np

class StatsCollector:
    def __init__(self):
        self.iter_stats = []
        self.best_cost = np.inf

    def updateIterStats(self, alg, interactive=True, anytime=True):
        self.iter_stats.append({'alg': alg.name,
                           'iteration': alg.curr_iteration,
                           'messages': alg.num_messages_sent,
                           'time': alg.curr_runtime,
                           'cost': alg.instance.cost()})

        if interactive:
            if alg.curr_iteration == 0:
                print('alg\titer\tmsgs\ttime\tcost')
            s = self.iter_stats[-1]
            self.best_cost = min(s['cost'], self.best_cost)
            print(s['alg'], s['iteration'], s['messages'], round(s['time'], 4),
                  self.best_cost if anytime else s['cost'], sep='\t\t')

    def printSummary(self, anytime=True):
        print('alg\titer\tmsgs\ttime\tcost')
        best_cost = np.inf
        for s in self.iter_stats:
            best_cost = min(s['cost'], best_cost)
            print(s['alg'], s['iteration'], s['messages'], round(s['time'], 4),
                  best_cost if anytime else s['cost'], sep='\t\t')