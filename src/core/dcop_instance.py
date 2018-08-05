import json
import os
import networkx as nx
import numpy as np

from core.variable import Variable
from core.constraint import Constraint
from core.agent import Agent
import itertools

class DCOPInstance:
    def __init__(self, filepath):
        self.data = None
        self.communication_graph = nx.DiGraph() # not used for now
        self.ccg_graph = nx.DiGraph()           # not used for now
        self.agents = {}
        self.variables = {}
        self.constraints = {}

        filename, extension = os.path.splitext(filepath)
        if extension == '.json':
            self._read_json(filepath)
        elif extension == '.xml':
            pass
        elif extension == '.ccg':
            self._read_ccg(filepath)
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
            all_tuples = list(itertools.product(*domains))
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
            for ai, aj in itertools.permutations(clique, 2):
                ai.addNeighbor(aj, self.constraints[con])


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

    def _read_ccg(self, filepath):
        """
            Line 1:
              p edges <N> <E>
            where
              p and edges are keywords
              <N> is the number of variables (integer)
              <E> is the total number of edges (integer)
            Variables:
              Have all binary domains. A unary constraint is associated to a variable and described as:
              v <v_id> <cost>
              where
                'v' is a keyword
                <v_id> is the ID of the variable
                <cost> is the cost associated to the choice: v = 1. When v = 0 , the cost = 0
            Edges:
              Each edge is described as:
              e <v1_id> <v2_id>
              where:
                'e' is a keyword
                <v1_id>, <v2_id> are the ID of the two nodes in the edge
                The constraint is : e(x1, x2) = INF if d1=d2=0; 0, otherwise.
             --- vertex types begin ---
             For each variable of the problem lists:
             <vid> <type>
                 where
                 <vid> is the variable ID
                 <type> \in {0, -,1, -2} denoting, respectively, a problem variable, and two auxiliary variables.
             --- vertex types end ---
        """
        with open(filepath) as f:
            content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content]
        line = content[0]
        _, _, nvars, nedges = line

        self.ccg_graph.add_nodes_from(range(nvars), type='decision_var', value=None)

        line_idx = 1
        while 'vertex types begin' not in line:
            line = content[line_idx]
            words = line.split()
            if words[0] == 'v':
                _, vid, cost = words
                self.ccg_graph.add_edge(vid, vid, weight=cost)
            if words[0] == 'e':
                _, vid1, vid2 = words
                self.ccg_graph.add_edge(vid1, vid2, weight=None)
            line_idx += 1
        line_idx += 1 # skip "vertex types begin"

        while 'vertex types end' not in line:
            line = content[line_idx]
            vid, type = line.split()
            self.ccg_graph.nodes().get(vid)['type'] = type
            line_idx += 1
        line_idx += 1 # skip "assignments begin"

        while 'assignments end' not in line:
            line = content[line_idx]
            vid, val = line.split()
            self.ccg_graph.nodes().get(vid)['value'] = type
            line_idx += 1


if __name__ == '__main__':
    #from utils.data import *
    data_path = '/Users/nando/Repos/DCOP/py_dcop/data/'
    dcopIstance = DCOPInstance(data_path + 'binary.json')
    print(dcopIstance)

    a = ['v1', 'v2', 'v0', 'v4', 'v3']
    print(sorted(a))