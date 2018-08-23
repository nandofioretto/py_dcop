import networkx as nx
import numpy as np

class DCOPGenerator:
    def __init__(self, seed=1234, filepath=None):
        self.filepath = filepath
        self.prng = np.random.RandomState(seed)

    def regular_grid(self, nnodes):
        G = nx.grid_graph([nnodes, nnodes]).to_undirected()
        while not nx.is_connected(G):
            G = nx.grid_graph(nnodes).to_undirected()

        # Normalize Graph
        Gn = nx.empty_graph(nnodes)
        map_nodes, nid = dict(), 0
        for n in G.nodes():
            map_nodes[n] = nid
            nid += 1
        for e in G.edges():
            Gn.add_edge(map_nodes[e[0]], map_nodes[e[1]])

        return Gn

    def scale_free(self, nnodes):
        G = nx.scale_free_graph(nnodes).to_undirected()
        while not nx.is_connected(G):
            G = nx.scale_free_graph(nnodes).to_undirected()
        return G

    def random_graph(self, nnodes, p1):
        assert 0 < p1 <= 1
        nedges = max(p1 * ((nnodes * (nnodes - 1)) / 2), nnodes)
        G = nx.Graph()
        nodes = list(range(nnodes))
        G.add_nodes_from(nodes)

        while G.number_of_edges() < nedges:
            u, v = sorted(self.prng.choice(nodes, size=2, replace=False))
            if not G.has_edge(u, v):
                G.add_edge(u, v)

        while not nx.is_connected(G):
            u, v = sorted(self.prng.choice(nodes, size=2, replace=False))
            if not G.has_edge(u, v):
                G.add_edge(u, v)

        return G