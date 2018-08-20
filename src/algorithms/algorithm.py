import numpy as np
import time
from utils.stats_collector import StatsCollector

class Algorithm:
    def __init__(self, name, dcop_instance, args, seed=1234):
        self.name = name
        self.instance = dcop_instance
        self.status = 'Initializing'
        self.iterations_limit = args['max_iter']
        self.curr_iteration = 0
        self.prng = np.random.RandomState(seed)
        self.num_messages_sent = 0
        self.curr_runtime = 0
        self.curr_cost = 0

    def run(self):
        start_time = time.time()
        for agtId in self.instance.agents:
            agt = self.instance.agents[agtId]
            self.onStart(agt)
        self.curr_runtime = time.time() - start_time
        StatsCollector.updateIterStats(self)

        while not self.terminationCondition():
            self.runIteration()
            self.curr_runtime = time.time() - start_time
            StatsCollector.updateIterStats(self)

        for agtId in self.instance.agents:
            agt = self.instance.agents[agtId]
            self.onTermination(agt)
            self.status == 'Finished'

    def runIteration(self):
        self.curr_iteration += 1

        for agtId in self.instance.agents:
            agt = self.instance.agents[agtId]
            self.onCycleStart(agt)
        for agtId in self.instance.agents:
            agt = self.instance.agents[agtId]
            self.onCurrentCycle(agt)
        for agtId in self.instance.agents:
            agt = self.instance.agents[agtId]
            self.onCycleEnd(agt)

    def onStart(self, agt):
        pass

    def onCycleStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        pass

    def onCycleEnd(self, agt):
        pass

    def onTermination(self, agt):
        pass

    def terminationCondition(self):
        return self.curr_iteration >= self.iterations_limit
