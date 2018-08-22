import xml.dom.minidom as md
import xml.etree.ElementTree as ET
import json
import commons as cm

def create_json_instance(name, agts, vars, doms, cons, fileout=''):
    """"
    It assumes constraint tables are complete
    """
    jagts = {}
    jvars = {}
    jcons = {}

    for vid in vars:
        v = vars[vid]
        d = doms[v['dom']]
        aid = v['agt']
        jvars['v'+vid] = {
            'value': None,
            'domain': d,
            'agent': 'a'+str(aid),
            'type': 1,
            'id': int(vid),
            'cons': []
        }

    for aid in agts:
        jagts['a'+aid] = {'vars': ['v'+vid for vid in vars if vars[vid]['agt'] == aid]}
        jagts['id'] = int(aid)

    for cid in cons:
        c = cons[cid]
        jcons['c'+cid] = {
            'scope': ['v'+vid for vid in c['scope']],
            'vals': [x['cost'] for x in c['values']]
        }
        for vid in c['scope']:
            jvars['v'+str(vid)]['cons'].append('c'+cid)

    instance = {'variables': jvars, 'agents': jagts, 'constraints': jcons}

    if fileout:
        #cm.save_json_file(fileout, instance)
        with open(fileout, 'w') as outfile:
            json.dump(instance, outfile, indent=2)
    else:
        print(json.dumps(instance, indent=2))


def sanity_check(vars, cons):
    """ Check all variables participate in some constraint """
    v_con = []
    for c in cons:
        for x in cons[c]['scope']:
            if x not in v_con:
               v_con.append(x)
    for v in vars:
        if v not in v_con:
            return False
    return True


if __name__ == '__main__':
    agts = {'1': None}
    vars = {'1': {'dom': '1', 'agt': '1'},
            '2': {'dom': '1', 'agt': '1'}}
    doms = {'1': [0, 1]}
    cons = {'1': {'arity': 2, 'def_cost': 0, 'scope': ['1', '2'],
                   'values': [{'tuple': [0, 0], 'cost': 1}, {'tuple': [0, 1], 'cost': 2},
                              {'tuple': [1, 0], 'cost': 5}, {'tuple': [1, 1], 'cost': 3}]}}


    create_xml_instance("test", agts, vars, doms, cons)
    create_wcsp_instance("test", agts, vars, doms, cons)
    create_json_instance("test", agts, vars, doms, cons)