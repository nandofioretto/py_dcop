import json
import os
import networkx as nx
import numpy as np
from itertools import product, permutations
from functools import reduce
import operator

from core.variable import Variable
from core.constraint import Constraint
from core.agent import Agent
import itertools

class DCOPInstance:
    def __init__(self, filepath=None):
        self.data = None
        self.agents = {}
        self.variables = {}
        self.constraints = {}
        if filepath is not None:
            filename, extension = os.path.splitext(filepath)
            if extension == '.json':
                self._read_json(filepath)
            elif extension == '.xml':
                pass
            elif extension == '.ccg':
                pass
            elif extension == '.wcsp':
                pass

    def cost(self):
        return np.sum(self.constraints[con].evaluate() for con in self.constraints)

    def _read_json(self, filepath):
        with open(filepath) as f:
            data = json.load(f)

        for varname in data['variables']:
            name = varname
            domain = data['variables'][varname]['domain']
            id = data['variables'][varname]['id']
            constr = data['variables'][varname]['cons']
            type = data['variables'][varname]['type']
            agent = data['variables'][varname]['agent']
            self.variables[name] = Variable(name=name, domain=domain, type='decision')

        for con in data['constraints']:
            name = con
            scope = data['constraints'][con]['scope']
            costs = data['constraints'][con]['vals']
            domains = [self.variables[vname].domain for vname in scope]
            all_tuples = list(product(*domains))
            assert(len(all_tuples) == len(costs))
            con_values = {all_tuples[i]: costs[i] for i in range(len(all_tuples))}

            self.constraints[name] = Constraint(name,
                                                scope=[self.variables[vid] for vid in scope],
                                                values=con_values)
            # add constriant to variables
            for vid in scope:
                self.variables[vid].addConstraint(self.constraints[name])

        for agt in data['agents']:
            name = agt
            var_names = data['agents'][agt]['vars']
            agt_constraints = []#list(set([c for c in self.variables[vid].constraints for vid in var_names]))
            for vid in var_names:
                for c in self.variables[vid].constraints:
                    if c not in agt_constraints:
                        agt_constraints.append(c)

            self.agents[name] = Agent(name,
                                      variables=[self.variables[vid] for vid in var_names],
                                      constraints=agt_constraints)
            for vid in var_names:
                self.variables[vid].setOwner(self.agents[name])

        # Connect neighbors:
        for con in self.constraints:
            clique = [var.controlled_by for var in self.constraints[con].scope]
            for ai, aj in permutations(clique, 2):
                ai.addNeighbor(aj, self.constraints[con])

    def generate_from_graph(self, G: nx.Graph, dsize, max_clique_size=np.inf,
                            cost_range=(0, 10), p2=1.0, def_cost=0, seed=1234):
        prng = np.random.RandomState(seed)

        # Generate Variables
        for n in G.nodes:
            vname = 'v_' + str(n)
            domain = list(range(dsize))
            self.variables[vname] = Variable(name=vname, domain=domain, type='decision')

        # Generate constraints - one for each clique
        cliques = list(nx.find_cliques(G))
        for i, c in enumerate(cliques):
            if len(c) > max_clique_size:
                print('Skipping constraints! Fix!')
                continue
            name = 'c_' + str(i)
            scope = ['v_' + str(ci) for ci in c]
            domains = [self.variables[vname].domain for vname in scope]
            all_tuples = product(*domains)
            n = reduce(operator.mul, map(len, domains), 1)
                                                                           costs = prng.randint(low=cost_range[0], high=cost_range[1], size=n)
            con_values = {T: costs[i] for i, T in enumerate(all_tuples)}
            # add constriant to variables
            for vid in scope:
                self.variables[vid].addConstraint(self.constraints[name])

        # Generate Agents
        for n in G.nodes:
            name, vid = 'a_' + str(n), 'v_' + str(n)
            agt_constraints = []
            for c in self.variables[vid].constraints:
                if c not in agt_constraints:
                    agt_constraints.append(c)
                    self.agents[name] = Agent(name, variables=[self.variables[vid]], constraints=agt_constraints)
            self.variables[vid].setOwner(self.agents[name])

        # Connect neighbors:
        for con in self.constraints:
            clique = [var.controlled_by for var in self.constraints[con].scope]
            for ai, aj in permutations(clique, 2):
                ai.addNeighbor(aj, self.constraints[con])

    def to_file(self, fileout):
        jout = {'constraints': {}, 'agents': {}, 'variables': {}}
        for agt in self.agents:
            jout['agents'][agt] = {'vars': [v.name for v in self.agents[agt].variables]}
        for i, var in enumerate(self.variables):
            jout['variables'][var] = {'id': i, 'cons': [c.name for c in self.variables[var].constraints],
                                      'domain': self.variables[var].domain,
                                      'type': 1,
                                      'value': None}
        for con in self.constraints:
            jout['constraints'][con] = {'vals': self.constraints[con].values.values(),
                                        'scope': self.constraints[con].scope}

    def __str__(self):
        s = '========== DCOP Instance ===========\n'
        for agt in self.agents:
            s += str(self.agents[agt]) + '\n'
        for con in self.constraints:
            s += str(self.constraints[con]) + '\n'
        for var in self.variables:
            s += str(self.variables[var]) + '\n'
        s += '====================================\n'
        return s

if __name__ == '__main__':
    #from utils.data import *
    data_path = '/Users/nando/Repos/DCOP/py_dcop/data/'
    dcopIstance = DCOPInstance(data_path + 'binary.json')
    print(dcopIstance)

    a = ['v1', 'v2', 'v0', 'v4', 'v3']
    print(sorted(a))