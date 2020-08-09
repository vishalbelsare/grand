from typing import Hashable, Generator
import networkx as nx


class NetworkXDialect(nx.Graph):
    """
    A NetworkXDialect provides a networkx-like interface for graph manipulation

    """

    def __init__(self, parent: "Graph"):
        self.parent = parent

    def add_node(self, name: Hashable, **kwargs):
        return self.parent.backend.add_node(name, kwargs)

    def nodes(self, data: bool = False):
        return self.parent.backend.all_nodes_as_generator(include_metadata=data)

    def add_edge(self, u: Hashable, v: Hashable, **kwargs):
        return self.parent.backend.add_edge(u, v, kwargs)

    def edges(self, data: bool = False):
        return self.parent.backend.all_edges_as_generator(include_metadata=data)

    def __getitem__(self, key):
        if not isinstance(key, (tuple, list)):
            return self.parent.backend.get_node_by_id(key)
        return self.parent.backend.get_edge_by_id(*key)


class CypherDialect:
    def __init__(self, parent: "Graph") -> None:
        self.parent = parent

    def query(self, query_text: str) -> any:
        """
        Perform a Cypher query on the current graph.

        Arguments:
            query_text (str): The cypher query text to run

        Returns:
            any

        """
        raise NotImplementedError()