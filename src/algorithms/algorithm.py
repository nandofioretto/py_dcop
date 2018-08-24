import numpy as np
import time
from utils.stats_collector import StatsCollector
from tqdm import tqdm

class Algorithm:
    def __init__(self, name, dcop_instance, args, seed=1234):
        self.name = name
        self.instance = dcop_instance
        self.status = 'Initializing'
        self.iterations_limit = args['max_iter']
        self.curr_iterations_limit = args['max_iter']
        self.curr_iteration = 0
        self.prng = np.random.RandomState(seed)
        self.num_messages_sent = 0
        self.curr_runtime = 0
        self.curr_cost = np.infty
        self.stats = StatsCollector()

    def reset(self, newseed):
        self.seed = newseed
        self.curr_iteration = 0
        self.prng = np.random.RandomState(newseed)
        self.num_messages_sent = 0
        self.curr_runtime = 0
        self.curr_cost = np.infty
        self.stats.reset()
        self.curr_iterations_limit = self.iterations_limit
        for var in self.instance.variables.values():
            var.setAssignment(0)

    def run(self, interactive=True, pbar=None, chain=False):
        # self.curr_iteration = 0
        # self.curr_cost = 0
        # self.num_messages_sent = 0
        if len(self.stats.iter_stats) > 0:
            self.curr_iteration = self.stats.iter_stats[-1]['iteration'] + 1
            self.num_messages_sent = self.stats.iter_stats[-1]['messages']
            self.curr_iterations_limit = self.curr_iteration + self.iterations_limit - 1
        off_time = 0 if self.curr_iteration == 0 else self.stats.iter_stats[-1]['time']


        start_time = time.time()
        for agtId in self.instance.agents:
            agt = self.instance.agents[agtId]
            self.onStart(agt)

        self.curr_runtime = time.time() - start_time + off_time
        self.stats.updateIterStats(self, interactive=interactive)

        while not self.terminationCondition():
            self.runIteration()
            self.curr_runtime = time.time() - start_time + off_time
            self.stats.updateIterStats(self, interactive=interactive)
            pbar.update(1)

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
        return self.curr_iteration >= self.curr_iterations_limit
