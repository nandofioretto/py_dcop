import networkx as nx


G1 = nx.DiGraph()
G1.add_nodes_from(['v1','v2','v3'], type='dec_var', weight=1, value=None)
G1.add_nodes_from(['a1', 'a2'], type='aux_var', weight=1, value=None)
G1.add_edge('v1', 'v2', w=-1)
G1.add_edge('v1', 'v3', w=-1)
G1.add_edge('v1', 'a1', w=-1)
G1.add_edge('v2', 'a2', w=-1)

G2 = nx.DiGraph()
G2.add_nodes_from(['v2','v3','v4'], type='dec_var', weight=1, value=None)
G2.add_nodes_from(['a3', 'a4'], type='aux_var', weight=1, value=None)
G2.add_edge('v3', 'v4', w=-1)
G2.add_edge('v2', 'a4', w=-1)
G2.add_edge('v2', 'a1', w=-1)
G2.add_edge('v4', 'a4', w=-1)


shared = [n for n in G1.nodes for m in G2.nodes if n == m and G1.nodes[n]['type'] == 'dec_var']

print(G1.edges)
# print(G2.edges)

# print(G2['v2'])
# print(list(G2.neighbors('v2')))
# for v in G2.neighbors('v2'):
#     print(G2.edges('v2', v))


print(G2.edges('v2'))
for e in G2.edges('v2'):
    G1.add_edge(e[0], e[1], w=G2.get_edge_data(*e)['w'])

for e in G1.edges():
    print(e, G1.get_edge_data(*e))

for u in shared:
    # assign it to G1
    G1.nodes[u]['weight'] += G2.nodes[u]['weight']

    for e in G2.edges(u):
        G1.add_edge(e[0], e[1], w=G2.get_edge_data(*e)['w'])

    G2.remove_node(u)

    # def _init_msgs(self, dcop):
    #     # Init messages (Tables):
    #     msg = {}
    #     for v in nodes:
    #         msg[v] = {}
    #
    #     for u, v in dcop.ccg_graph.edges():
    #         if u != v:
    #             msg[u][v] = (0, 0)
    #     return msg
    #
    # def solve(self, dcop):
    #     g = dcop.ccg_graph
    #     # todo: set initial variable value at random (0,1)
    #     msg = self._init_msgs(dcop)
    #
    #     for u in g.nodes():
    #         tab = [0, 0]
    #         tab2= [0, 0]
    #         if g.has_edge(u, u):
    #             tab[0] = g.get_edge_data(u, u)['weight']
    #             tab[1] = g.get_edge_data(u, u)['weight']
    #
    #         for v in g.neighbors(u):
    #             if v != u:
    #                 tab[0] += msg[v][u][1]
    #                 tab2[0] += msg[v][u][0]
    #                 tab2[1] += msg[v][u][1]
    #
    #         for e in g.edges()