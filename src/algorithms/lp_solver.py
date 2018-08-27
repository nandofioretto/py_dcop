import numpy as np
import networkx as nx
from gurobi import *

from algorithms.algorithm import Algorithm
from utils.ccg_utils import transform_dcop_instance_to_ccg, set_var_value

class LPSolver(Algorithm):
    def __init__(self, name, dcop_instance, args={'max_iter:': 1, 'relax':False}, seed=1234):
        super(LPSolver, self).__init__(name, dcop_instance, args, seed)

        self.relax = args['relax']
        self.ccg = transform_dcop_instance_to_ccg(dcop_instance)
        self.root = min([aname for aname in dcop_instance.agents])

        self.values = {u: 0 for u in self.ccg.nodes()}
        self.variables = dcop_instance.variables.values()
        self.var_ccg_nodes = {vname : [(u, data['rank']) for u, data in self.ccg.nodes(data=True)
                                                         if ('variable' in data and data['variable'] == vname)]
                                for vname in dcop_instance.variables}


    def onStart(self, agt):
        # First Iteration: Set random assignment
        agt.setRandomAssignment()

        if agt.name is self.root:
            for u in self.ccg.nodes():
                self.values[u] = self.prng.randint(0, 1)

    def onCycleStart(self, agt):
        pass

    def onCurrentCycle(self, agt):
        if agt.name is not self.root:
            return

        ccg = self.ccg
        weights = nx.get_node_attributes(ccg, 'weight')

        N = ccg.number_of_nodes()
        model = Model()
        if self.relax:
            X = model.addVars(ccg.nodes(), lb=[0]*N, ub=[1]*N, vtype=GRB.CONTINUOUS)
        else:
            X = model.addVars(ccg.nodes(), vtype=GRB.BINARY)

        # Constraints: (for any adjiecent vertices)
        for u, v in ccg.edges():
            model.addConstr(X[u] + X[v] >= 1)

        obj = None
        for u in ccg.nodes():
            obj += weights[u] * X[u]

        self.gurobiSolve(model, obj)

        for u in ccg.nodes():
            self.values[u] = X[u].x

        print('0 count:', list(self.values.values()).count(0), '/', N)
        print('1 count:', list(self.values.values()).count(1), '/', N)


    def gurobiSolve(self, model, obj):
        model.setObjective(obj)
        model.setParam('OutputFlag', False)
        model.setParam('OptimalityTol', 1e-6)
        model.optimize()
        if model.status != 2 and model.status != 13:
            print('Gurobi status:', model.status)
        return model.status


    def onCycleEnd(self, agt):
        if agt.name != self.root:
            return

        ccg = self.ccg
        vertex_cover = [u for u in ccg.nodes() if self.values[u] >= 0.5]
        for var in self.variables:
            set_var_value(var, vertex_cover, self.var_ccg_nodes[var.name], self.prng)
