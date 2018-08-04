"""
Schema:

For every agent
    1. send messages to all neighbrs. In the message include the following:
"""


class CCGMaxSum:
    def __init__(self):
        pass

    def _init_msgs(self, dcop):
        # Init messages (Tables):
        msg = {}
        for v in nodes:
            msg[v] = {}

        for u, v in dcop.ccg_graph.edges():
            if u != v:
                msg[u][v] = (0, 0)
        return msg

    def solve(self, dcop):
        g = dcop.ccg_graph
        # todo: set initial variable value at random (0,1)
        msg = self._init_msgs(dcop)

        for u in g.nodes():
            tab = [0, 0]
            tab2= [0, 0]
            if g.has_edge(u, u):
                tab[0] = g.get_edge_data(u, u)['weight']
                tab[1] = g.get_edge_data(u, u)['weight']

            for v in g.neighbors(u):
                if v != u:
                    tab[0] += msg[v][u][1]
                    tab2[0] += msg[v][u][0]
                    tab2[1] += msg[v][u][1]

            for e in g.edges()