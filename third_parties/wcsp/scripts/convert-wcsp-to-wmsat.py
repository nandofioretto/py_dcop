#!/usr/bin/python3

# Convert WCSP in DIMACS format to Weighted Max-SAT in DIMACS format
# <http://maxsat.ia.udl.cat/requirements/>
#
# Usage: ./convert-wcsp-to-wmsat.py < /path/to/wcsp

# Currently only domain size = 2 can be handled

class Clause:
    def __init__(self, variables, weight):
        self.variables = variables
        self.weight = weight

import sys

first_line = True
second_line = True
num_variables = 0
max_domain_size = 0
num_constraints = 0
variable_domain_size = []
clauses = []

# read the WCSP from stdin
lines = sys.stdin.readlines()
i = 0
while i < len(lines):  # we can't use for-loop here because we need to jump i within the loop
    line = lines[i]

    line = line.strip()

    # skip blank and comment lines
    if not line or line.startswith('c'):
        continue

    # first line: problem_name number_of_variables max_domain_size number_of_constraints
    if first_line:

        first_line = False

        _, num_variables, max_domain_size, num_constraints, _ = line.split()
        num_variables = int(num_variables)
        max_domain_size = int(max_domain_size)
        num_constraints = int(num_constraints)

        i += 1
        continue

    # the domain size of each variable
    if second_line:

        second_line = False

        variable_domain_size = [int(s) for s in line.split()]

        i += 1
        continue

    # a constraint line
    constraint = line.split()
    arity = int(constraint[0])
    variables = [int(v)+1 for v in constraint[1:2+arity]]
    # TODO: default_cost is currently always assumed to be 0
    default_cost = int(constraint[-2])
    default_cost = 0
    num_specified_costs = int(constraint[-1])

    for j in range(num_specified_costs):
        i += 1
        l = lines[i].split()

        # all the variables are here
        clauses.append(
            Clause([variables[k] if int(l[k]) > 0 else -variables[k] for k in range(len(l)-1)],
                   l[-1]))

    i += 1


# print the MaxSAT file
print('p wcnf {} {}'.format(num_variables, len(clauses)))
for c in clauses:
    print(c.weight, end=' ')
    for v in c.variables:
        print(v, end=' ')
    print('0')
