

iter_stats = []

class StatsCollector:

    @staticmethod
    def updateIterStats(alg):
        iter_stats.append({'iteration': alg.curr_iteration,
                           'messages': alg.num_messages_sent,
                           'time': alg.curr_runtime,
                           'cost': alg.instance.cost()})

    @staticmethod
    def printSummary():
        print('iter\tmsgs\ttime\tcost')
        for s in iter_stats:
            print(s['iteration'], s['messages'], round(s['time'], 4), s['cost'], sep='\t\t')