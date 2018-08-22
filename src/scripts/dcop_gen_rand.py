import random
import itertools
import json
from scipy.special import comb
import sys, getopt, os
import dcop_instance as dcop

def generate(nagts, dsize, p1, p2, cost_range=(0, 10), max_arity=2, def_cost = 0, int_cost=True, outfile='') :
    assert (0.0 < p1 <= 1.0)
    assert (0.0 < p2 <= 1.0)
    agts = {}
    vars = {}
    doms = {'0': list(range(0, dsize))}
    cons = {}

    for i in range(0, nagts):
        agts[str(i)] = None
        vars[str(i)] = {'dom': '0', 'agt': str(i)}

    ncons = int(p1 * ((nagts*(nagts-1)) / 2))
    constraint_set = set()

    consumed_constr = 0
    cid = 0
    while consumed_constr < ncons:
        arity = random.randint(*(2, max_arity))
        scope = frozenset(random.sample(range(nagts), arity))
        # Don't duplicate.
        if scope in constraint_set:
            continue

        cons[str(cid)] = {'arity': arity, 'def_cost': def_cost,
                          'scope': [str(x) for x in scope], 'values': []}
        for assignments in itertools.product(*([[0, 1], ] * arity)):
            val = {'tuple': []}
            val['tuple'] = list(assignments)
            if random.uniform(0,1) < p2:
            	if int_cost:
            		val['cost'] = random.randint(*cost_range)
            	else:
            		val['cost'] = random.uniform(*cost_range)
            else:
            	val['cost'] = 500000
            cons[str(cid)]['values'].append(val)

        constraint_set.add(scope)
        consumed_constr += int(comb(arity, 2))
        cid += 1

    return agts, vars, doms, cons


def main(argv):
    agts = 0
    doms = 2
    p1 = 1.0
    max_arity = 2
    max_cost = 10
    out_file = ''
    name = ''
    def rise_exception():
        print('Input Error. Usage:\nmain.py -a -d -p -r -c -n -o <outputfile>')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "a:d:p:r:c:n:o:h",
                                   ["agts=", "doms=", "p1=", "max_arity=", "max_cost=",
                                    "name=", "ofile=", "help"])
    except getopt.GetoptError:
        rise_exception()
    if len(opts) != 7:
        rise_exception()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('main.py -i <inputfile> -o <outputfile>')w
            sys.exit()
        elif opt in ('-a', '--agts'):
            agts = int(arg)
        elif opt in ('-d', '--doms'):
            doms = int(arg)
        elif opt in ('-p', '--p1'):
            p1 = float(arg)
        elif opt in ('-r', '--max_arity'):
            max_arity = int(arg)
        elif opt in ('-c', '--max_cost'):
            max_cost = int(arg)
        elif opt in ("-n", "--name"):
            name = arg
        elif opt in ("-o", "--ofile"):
            out_file = arg
    return agts, doms, p1, max_arity, max_cost, name, out_file


if __name__ == '__main__':
    nagts, dsize, p1, maxarity, maxcost, name, outfile = main(sys.argv[1:])

    agts, vars, doms, cons = generate(nagts=nagts, dsize=dsize, p1=p1, p2=0.99,
                                      cost_range=(0,maxcost),
                                      max_arity=maxarity, def_cost=0)

    if not dcop.sanity_check(vars, cons):
        print("sanity check failed!")
        exit(-1)

    print('Creating DCOP instance' + name)
    dcop.create_xml_instance(name, agts, vars, doms, cons, outfile+'.xml')
    dcop.create_wcsp_instance(name, agts, vars, doms, cons, outfile+'.wcsp')
    dcop.create_json_instance(name, agts, vars, doms, cons, outfile+'.json')
