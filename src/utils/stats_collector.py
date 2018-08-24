import numpy as np
import pandas as pd


class StatsCollector:
    best_cost = np.inf
    iter_stats = []

    @staticmethod
    def reset():
        StatsCollector.iter_stats = []
        StatsCollector.best_cost = np.inf

    @staticmethod
    def updateIterStats(alg, interactive=True, anytime=True):
        StatsCollector.iter_stats.append({'alg': alg.name,
                           'iteration': alg.curr_iteration,
                           'messages': alg.num_messages_sent,
                           'time': alg.curr_runtime,
                           'cost': alg.instance.cost()})

        if interactive:
            if alg.curr_iteration == 0:
                print('alg\titer\tmsgs\ttime\tcost')
            s = StatsCollector.iter_stats[-1]
            StatsCollector.best_cost = min(s['cost'], StatsCollector.best_cost)
            print(s['alg'], s['iteration'], s['messages'], round(s['time'], 4),
                  StatsCollector.best_cost if anytime else s['cost'], sep='\t\t')

    @staticmethod
    def printSummary(anytime=True):
        print('alg\titer\tmsgs\ttime\tcost')
        best_cost = np.inf
        for s in StatsCollector.iter_stats:
            best_cost = min(s['cost'], best_cost)
            print(s['alg'], s['iteration'], s['messages'], round(s['time'], 4),
                  best_cost if anytime else s['cost'], sep='\t\t')

    @staticmethod
    def getDataFrameSummary(anytime=True):
        if anytime:
            best_cost, costs = np.inf, []
            for s in StatsCollector.iter_stats:
                best_cost = min(s['cost'], best_cost)
                costs.append(best_cost)
        else:
            costs = [s['cost'] for s in StatsCollector.iter_stats]

        return pd.DataFrame(
            {'alg': [s['alg'] for s in StatsCollector.iter_stats],
             'iter': [s['iteration'] for s in StatsCollector.iter_stats],
             'msgs': [s['messages'] for s in StatsCollector.iter_stats],
             'time': [s['time'] for s in StatsCollector.iter_stats],
             'cost': costs
             })