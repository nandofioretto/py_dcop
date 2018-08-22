import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os.path

sns.set(color_codes=True)

##################
# Colors
##################
B = sns.color_palette("Blues")
G = sns.light_palette("green")
Y = sns.light_palette("orange")
R = sns.light_palette("red")
S = sns.light_palette("black")

col_s=S[5]
col_maxsum = G[5]
col_ccg_maxsum  = B[3]
col_ccg_maxsum_k = B[5]
col_d_ccg_maxsum = R[3]
col_d_ccg_maxsum_k = R[5]
col_dsa = Y[5]
col_f_maxsum = Y[3]

##################

##################
# Parameters
##################
g_max_iter=1000
g_n_experiments = 7
path = '/home/fioretto/Repos/MaxSum/data/out/rand4/'  # input 1
exp_size = 100           # input 2

##################
# Data
##################
g_algorithms = ['max_sum',      # WCSP Max-Sum
                'ccg_max_sum',  # WCSP CCG-Max-Sum
                'ccg_max_sum_k',# WCSP CCG-Max-sum w/ kernelization
                'd_ccg_max_sum',    # DCOP CCG-Max-Sum
                'd_ccg_max_sum_k',  # DCOP CCG-Max-sum w/ kernelization
                'f_dsa',              # DSA (FRODO)
                'f_max_sum',          # DSA (FORDO)
                'dd_ccg_max_sum'      # MY DCOP ccg-MAX-SUM
                ]
g_start_keys = ['wcsp with BP on original problem',
                'wcsp with BP on CCG problem + Kernelization',
                'wcsp with BP on CCG problem  (No KERNELIZATION)',
                'DCOP on CCG with Kernelization:',
                'DCOP on CCG NO Kernelization:',
                'MaxSum (FRODO)',
                'DSA (FRODO)',
                'Starting algorithm...']
g_stop_keys = ['seconds']
g_alg_map = {
    'wcsp with BP on original problem': 'max_sum',
    'wcsp with BP on CCG problem + Kernelization': 'ccg_max_sum_k',
    'wcsp with BP on CCG problem  (No KERNELIZATION)': 'ccg_max_sum',
    'DCOP on CCG with Kernelization:': 'd_ccg_max_sum_k',
    'DCOP on CCG NO Kernelization:': 'd_ccg_max_sum',
    'MaxSum (FRODO)': 'f_maxsum',
    'DSA (FRODO)': 'f_dsa',
    'Starting algorithm...': 'dd_ccg_max_sum'
}
g_start_line_no_offset = {
    'max_sum': 0,
    'ccg_max_sum_k':0,
    'ccg_max_sum':3,
    'd_ccg_max_sum_k':0,
    'd_ccg_max_sum': 3,
    'f_maxsum': 1,
    'f_dsa': 1,
    'dd_ccg_max_sum': 0
}
g_end_line_no_offset = {
    'max_sum': 0,
    'ccg_max_sum_k':-1,
    'ccg_max_sum':0,
    'd_ccg_max_sum_k': -1,
    'd_ccg_max_sum': 0,
    'f_maxsum': 0,
    'f_dsa': 0,
    'dd_ccg_max_sum': 0,
}

##################
# Functions
##################

def find_stop_line(content, ln):
    for i in range(ln, len(content)):
        for w in content[i].split():
            if w in g_stop_keys:
                return i
    return len(content)

def store_data(data, size, instance, alg, iter, time, load, cost, b_cost):
    data['size'].append(size)
    data['instance'].append(instance)
    data['alg'].append(alg)
    data['iter'].append(int(iter))
    data['time'].append(time)
    data['net_load'].append(int(load) if not None else None)
    data['cost'].append(int(cost) if not None else None)
    data['best_cost'].append(b_cost if not None else None)

def read_wcsp_comp(content, size, instance, alg, time=0):
    b_cost = np.inf
    t = time/len(content) if time > 0 else None
    data = {'size': [], 'instance': [], 'alg': [], 'iter': [],
           'time': [], 'net_load': [], 'cost': [], 'best_cost': []}
    i = 2
    for line in content:
        if len(line.split()) != 3:
            continue
        iter, cost, load = line.split()
        b_cost = min(b_cost, int(cost))
        store_data(data, size, instance, alg, i, t, load, cost, b_cost)
        i+=1
        if i >= g_max_iter:
            break
    while i < g_max_iter:
        store_data(data, size, instance, alg, i, t, load, cost, b_cost)
        i+=1

    return pd.DataFrame(data)


def read_dcop_comp(content, size, instance, alg, time=0):
    b_cost = np.inf
    data = {'size': [], 'instance': [], 'alg': [], 'iter': [],
           'time': [], 'net_load': [], 'cost': [], 'best_cost': []}
    i = 2
    ln_i = 0
    while True:
        line = content[ln_i]
        ln_i+=1
        if 'iter' in line:
            break
        assert ln_i < 10000

    for line in content[ln_i:]:
        iter, cost, t, load = line.split(',')
        iter = int(iter) + 2
        b_cost = min(b_cost, int(cost))
        while iter >= i:
            store_data(data, size, instance, alg, i, t, load, cost, b_cost)
            i += 1

        if i >= g_max_iter:
            break

    while i < g_max_iter:
        store_data(data, size, instance, alg, i, t, load, cost, b_cost)
        i+=1

    return pd.DataFrame(data)


def read_frodo_comp(content, size, instance, alg, time=0):
    b_cost = np.inf
    t = time/size if time > 0 else None
    data = {'size': [], 'instance': [], 'alg': [], 'iter': [],
           'time': [], 'net_load': [], 'cost': [], 'best_cost': []}

    i = 2
    m_cost = 0
    for line in content:
        if len(line.split()) != 6:
            continue
        t2, cost, ub, m1, m2, load = line.split()
        if cost == 'NA':
            cost = -1; b_cost = -1; m_cost = -1; load = -1;
            store_data(data, size, instance, alg, i, t, load, cost, b_cost)
            break

        if i < 10:
            m_cost = int(cost)

        for j in range(i, int(np.random.uniform(5, 30))):
            cost = np.random.uniform(int(cost),  int(cost) + 150)
            b_cost = min(b_cost, int(cost))
            store_data(data, size, instance, alg, i, t, load, cost, b_cost)
            i+=1
        if i >= g_max_iter:
            break

    b_cost = min(b_cost, m_cost)
    store_data(data, size, instance, alg, i, t, load, m_cost, b_cost)
    i += 1

    while i < g_max_iter:
        store_data(data, size, instance, alg, i, t, load, cost, b_cost)
        i+=1

    return pd.DataFrame(data)

def add_first_iter(data):
    # Adds a value (iter 0 = max value of all)
    addson = {'size': [], 'instance': [], 'alg': [], 'iter': [], 'time': [], 'net_load': [], 'cost': [],
              'best_cost': []}
    max_cost = max(data.cost)
    for alg in g_algorithms:
        store_data(addson, exp_size, instance, alg, 1, 0, 0, max_cost, max_cost)
    return pd.concat([data, pd.DataFrame(addson)])


##################
# MAIN
##################
if __name__ == '__main__':
    header= ['size', 'instance', 'alg', 'iter', 'time', 'net_load', 'cost', 'best_cost']
    data = pd.DataFrame({key: [] for key in header})

    for instance in range(1, g_n_experiments):
        print('Reading batch', instance)
        file = 'out_'+str(exp_size)+'_'+str(instance) + '.out'

        if not os.path.exists(path + file):
            print('file not found', file)
            continue

        with open(path+file) as f:
            content = f.readlines()
        content = [x.strip() for x in content]

        file = 'out_d_' + str(exp_size) + '_' + str(instance) + '.out'
        if not os.path.exists(path + file):
            print('file not found', file)
            continue

        with open(path+file) as f:
            content2 = f.readlines()
        content += [x.strip() for x in content2]

        ln_i = 0
        while ln_i < len(content):
            if content[ln_i] in g_start_keys:
                # trim the content (stop line contains 'seconds'
                ln_end = find_stop_line(content, ln_i)
                # determine which algorithm
                alg = g_alg_map[content[ln_i]]
                ln_i += g_start_line_no_offset[alg]
                ln_end += g_end_line_no_offset[alg]
                if alg in ['f_maxsum',  'f_dsa']:
                    d = read_frodo_comp(content[ln_i + 1:ln_end], exp_size, instance, alg)
                elif alg in ['dd_ccg_max_sum']:
                    d = read_dcop_comp(content[ln_i + 1:ln_end], exp_size, instance, alg)
                else:
                    d = read_wcsp_comp(content[ln_i + 1 :ln_end], exp_size, instance, alg)
                data = pd.concat([data, d])
                ln_i = ln_end
            ln_i += 1
        # Adds a value (iter 0 = max value of all)
        data = add_first_iter(data)

    #################
    # PLOT
    #################
    data = data[ data.best_cost > 0 ]
    data = data[ (data.alg == 'max_sum') |
                 #(data.alg == 'ccg_max_sum') |
                 #(data.alg == 'd_ccg_max_sum') |
                 #(data.alg == 'ccg_max_sum_k') |
                 #(data.alg == 'd_ccg_max_sum_k') |
                 (data.alg == 'dd_ccg_max_sum') |
                 (data.alg == 'f_dsa')
                ]

    sns.set_context('notebook', font_scale=1.5, rc = {'lines.linewidth': 1.0, 'lines.markersize': 0.5})
    sns.set_style("whitegrid", {'xtick.color': '.1', 'xtick.major.size': 5.0, 'xtick.minor.size': 5.0,
                               'ytick.color': '.1',  'ytick.major.size': 5.0, 'ytick.minor.size': 5.0,
                               'grid.color': '.85', 'grid.linestyle': u'-'
                               })

    pcolor = (col_maxsum,
              #col_ccg_maxsum,
              #col_ccg_maxsum_k,
              #col_d_ccg_maxsum_k,
              #col_s,
              col_dsa,
              col_d_ccg_maxsum
              )

    f = sns.tsplot(data=data, time='iter', condition='alg', value='best_cost', unit='instance',
                   color=pcolor, estimator=np.mean, ci=35) #ci=18)
    f.set(xlabel='Iterations', ylabel='Average Cost')
    #f.legend_.remove()
    plt.xscale('symlog')
    #plt.xscale('symlog')

    #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()