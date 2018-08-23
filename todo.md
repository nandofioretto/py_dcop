- [x] Implement CCG DSA

    Prior doing the following check the size of the sub-problem of the agents -- how many local variables, how many
    shared variables?
- [x] Try to start CCG from DSA initialization
- [x] Speed up CCG MAx sum (set_var_value) by memoring at the beginning the nodes of the CCG which are 
     assicuated to the specific variable var:
     var_ccg_nodes[var.name] = [(u, data['rank']) for u, data in ccg.nodes(data=True) 
                                if ('variable' in data and data['variable'] == var.name) ]
     In ser_var_value do:
     node_rank_pairs = [r  for (u, r) in var_ccg_nodes[var.name] if u not in VC]
- [ ] Fix handling n-ary constraints in the problem definition (some problem with neighbors)


- [] Implement version of CCG-maxsum where agents only take pointers to the nodes
- [] Implement version of CCG-maxsum / dsa where agents use gurobi to solve local problems and exchange messages
     only with their neighbors to try to minimize conflicts.
