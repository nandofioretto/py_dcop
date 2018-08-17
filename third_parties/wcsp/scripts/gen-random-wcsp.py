#!/usr/bin/python3

# Generate random WCSP instances.

import random
import itertools

integer_cost = True
arity_range = (2,4)
num_variables = 500
num_constaints = 1000
cost_range = (0, 10)

print('unknown {} 2 {} 99999'.format(num_variables, num_constaints))
print('2 ' * num_variables)

constraint_set = set()

for _ in range(num_constaints):
    arity = random.randint(*arity_range)
    print(arity, end=' ')

    while True:
        variables = frozenset(random.sample(range(num_variables), arity))

        # Don't duplicate.
        if variables not in constraint_set:
            break

    constraint_set.add(variables)
    print(' '.join(str(i) for i in variables), end=' ')
    print('0 {}'.format(2 ** arity))

    for assignments in itertools.product(*([[0, 1],] * arity)):
        print(' '.join(str(i) for i in assignments), end=' ')
        if integer_cost:
            print(random.randint(*cost_range))
        else:
            print(random.uniform(*cost_range))
