#!/usr/bin/python3

# convert UAI format to WCSP
# Usage: python3 convert-uai-to-wcsp.py < input.uai > output.wcsp

L=1e10

# C++ like stream input
def read_tokens(f):
   for line in f:
       for token in line.split():
           yield token

from sys import stdin
from math import log

stdin.readline()  # ignore first line MARKOV

nv = int(stdin.readline())  # second line: number of variables

# third line: arity
domain_sizes = [int(i) for i in stdin.readline().split()]

assert(len(domain_sizes) == nv)

# fourth line: number of cliques/constraints
nc = int(stdin.readline())

assert(max(domain_sizes) == 2)

print('uai {} {} {} 99999'.format(nv, max(domain_sizes), nc))
print(' '.join(str(x) for x in domain_sizes))

tokens = read_tokens(stdin)

constraints = []

# collect the variables in each constraint
for i in range(nc):

    arity = int(next(tokens))

    variables = [None for j in range(arity)]

    for j in range(arity):
        variables[arity - j - 1] = int(next(tokens))

    constraints.append(variables)

# collect the cost in each constraint
for i in range(nc):

    arity = len(constraints[i])
    ntuples = int(next(tokens))  # number of entries

    print(arity, end=' ')
    for v in constraints[i]:
        print(v, end=' ')
    print('0 {}'.format(ntuples))

    costs = []
    s = 0.0

    for j in range(ntuples):
        cost = float(next(tokens))
        s += cost
        costs.append(cost)

    # load the entries in the constraint
    for j in range(ntuples):
        for k in range(len(constraints[i])):
            if j & (1 << k):
                print(1, end=' ')
            else:
                print(0, end=' ')

        cost = -log(costs[j] / s)
        if cost == float('Inf'):
            cost = L
        print(cost)
