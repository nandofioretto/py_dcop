import json
import os
import networkx as nx
import numpy as np
from itertools import product, permutations, combinations
from functools import reduce
import operator
from tqdm import tqdm

from core.variable import Variable
from core.constraint import Constraint
from core.agent import Agent

class DCOPInstance:
    def __init__(self, seed=1234, filepath=None):
        self.data = None
        self.prng = np.random.RandomState(seed)
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
                            cost_range=(0, 10), p2=1.0, def_cost=np.infty):
        """
        Generate a dcop instance from a Graph topology.
        Merges all cliques up to size :param max_clique_size
        :param G:
        :param dsize:
        :param max_clique_size:
        :param cost_range:
        :param p2:
        :param def_cost:
        :param seed:
        :return:
        """
        # Generate Variables
        for n in G.nodes():
            self._create_variables(n, dsize)

        # Generate constraints - one for each clique
        i = 0
        # with tqdm(total=G.number_of_edges()) as pbar:
        for clique in nx.find_cliques(G):
            clique = sorted(clique)
            if len(clique) <= max_clique_size:
                self._create_constraint('c_' + str(i), clique, cost_range, p2, def_cost)
                i += 1
                # pbar.update(len(list(combinations(clique, 2))))
            else:
                for bincon in combinations(clique, 2):
                    self._create_constraint('c_' + str(i), bincon, cost_range, p2, def_cost)
                    i += 1
                    # pbar.update(1)

        # Generate Agents
        for n in G.nodes():
            self._create_agents(n)

        # Connect neighbors:
        for con in self.constraints:
            agt_clique = [var.controlled_by for var in self.constraints[con].scope]
            for ai, aj in permutations(agt_clique, 2):
                ai.addNeighbor(aj, self.constraints[con])

    def _create_variables(self, n, dsize):
        vname = 'v_' + str(n)
        domain = list(range(dsize))
        self.variables[vname] = Variable(name=vname, domain=domain, type='decision')

    def _create_constraint(self, name, clique, cost_range, p2=1.0, def_cost=np.infty):
        scope = ['v_' + str(ci) for ci in clique]
        domains = [self.variables[vname].domain for vname in scope]
        all_tuples = product(*domains)
        n = reduce(operator.mul, map(len, domains), 1)
        costs = self.prng.randint(low=cost_range[0], high=cost_range[1], size=n).astype(float)
        violations = int((1-p2) * n)
        for i in self.prng.randint(low=0, high=n, size=violations):
            costs[i] = def_cost
        con_values = {T: costs[i] for i, T in enumerate(all_tuples)}
        self.constraints[name] = Constraint(name,
                                            scope=[self.variables[vname] for vname in scope],
                                            values=con_values)
        # add constriant to variables
        for vid in scope:
            self.variables[vid].addConstraint(self.constraints[name])

    def _create_agents(self, n):
        name, vid = 'a_' + str(n), 'v_' + str(n)
        self.agents[name] = Agent(name, variables=[self.variables[vid]],
                                  constraints=self.variables[vid].constraints)
        self.variables[vid].setOwner(self.agents[name])

    def to_file(self, fileout):
        """
        Write dcop instance to file as a json file
        :param fileout:
        :return:
        """
        jout = {'constraints': {}, 'agents': {}, 'variables': {}}
        for a in self.agents:
            agt = self.agents[a]
            jout['agents'][a] = {'vars': [v.name for v in agt.variables]}

        for i, v in enumerate(self.variables):
            var = self.variables[v]
            jout['variables'][v] = {'id': i, 'cons': [c.name for c in var.constraints],
                                    'domain': var.domain, 'type': 1, 'value': None,
                                    'agent': var.controlled_by.name}

        for c in self.constraints:
            con = self.constraints[c]
            jout['constraints'][c] = {'vals': [int(v) for v in con.values.values()],
                                      'scope': [v.name for v in con.scope]}

        print('Writing dcop instance on file', fileout)
        with open(fileout, 'w') as fp:
            json.dump(jout, fp, sort_keys=True, indent=4)

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
