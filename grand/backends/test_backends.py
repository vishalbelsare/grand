import pytest
import os

import networkx as nx

from . import NetworkXBackend, SQLBackend, DynamoDBBackend
from .. import Graph


@pytest.mark.parametrize(
    "backend",
    [
        pytest.param(
            SQLBackend,
            marks=pytest.mark.skipif(
                os.environ.get("TEST_NETWORKXBACKEND", default="1") != "1",
                reason="NetworkX Backend skipped because $TEST_NETWORKXBACKEND != 0.",
            ),
        ),
        pytest.param(
            SQLBackend,
            marks=pytest.mark.skipif(
                os.environ.get("TEST_SQLBACKEND", default="1") != "1",
                reason="SQL Backend skipped because $TEST_SQLBACKEND != 0.",
            ),
        ),
        pytest.param(
            DynamoDBBackend,
            marks=pytest.mark.skipif(
                os.environ.get("TEST_DYNAMODBBACKEND") != "1",
                reason="DynamoDB Backend skipped because $TEST_DYNAMODBBACKEND != 0.",
            ),
        ),
    ],
)
class TestSQLBackend:
    def test_can_create(self, backend):
        backend()

    def test_can_add_node(self, backend):
        G = Graph(backend=backend())
        nxG = nx.Graph()
        G.nx.add_node("A", k="v")
        nxG.add_node("A", k="v")
        assert len(G.nx.nodes()) == len(nxG.nodes())
        G.nx.add_node("B", k="v")
        nxG.add_node("B", k="v")
        assert len(G.nx.nodes()) == len(nxG.nodes())

    def test_can_add_edge(self, backend):
        G = Graph(backend=backend())
        nxG = nx.Graph()
        G.nx.add_edge("A", "B")
        nxG.add_edge("A", "B")
        assert len(G.nx.edges()) == len(nxG.edges())
        G.nx.add_edge("A", "B")
        nxG.add_edge("A", "B")
        assert len(G.nx.edges()) == len(nxG.edges())

    def test_can_get_node(self, backend):
        G = Graph(backend=backend())
        nxG = nx.Graph()
        md = dict(k="B")
        G.nx.add_node("A", **md)
        nxG.add_node("A", **md)
        assert G.nx.nodes["A"] == nxG.nodes["A"]

    def test_can_get_edge(self, backend):
        G = Graph(backend=backend())
        nxG = nx.Graph()
        md = dict(k="B")
        G.nx.add_edge("A", "B", **md)
        nxG.add_edge("A", "B", **md)
        assert G.nx.get_edge_data("A", "B") == nxG.get_edge_data("A", "B")

    def test_can_get_neighbors(self, backend):
        G = Graph(backend=backend())
        nxG = nx.Graph()
        G.nx.add_edge("A", "B")
        nxG.add_edge("A", "B")
        assert sorted([i for i in G.nx.neighbors("A")]) == sorted(
            [i for i in nxG.neighbors("A")]
        )
        assert sorted([i for i in G.nx.neighbors("B")]) == sorted(
            [i for i in nxG.neighbors("B")]
        )
        G.nx.add_edge("A", "C")
        nxG.add_edge("A", "C")
        assert sorted([i for i in G.nx.neighbors("A")]) == sorted(
            [i for i in nxG.neighbors("A")]
        )
        assert sorted([i for i in G.nx.neighbors("B")]) == sorted(
            [i for i in nxG.neighbors("B")]
        )
        assert sorted([i for i in G.nx.neighbors("C")]) == sorted(
            [i for i in nxG.neighbors("C")]
        )

    def test_undirected_adj(self, backend):
        G = Graph(backend=backend())
        nxG = nx.Graph()
        assert G.nx._adj == nxG._adj
        G.nx.add_edge("A", "B")
        nxG.add_edge("A", "B")
        assert G.nx._adj == nxG._adj

    def test_directed_adj(self, backend):
        G = Graph(backend=SQLBackend(directed=True))
        nxG = nx.DiGraph()
        assert G.nx._adj == nxG._adj
        G.nx.add_edge("A", "B")
        nxG.add_edge("A", "B")
        assert G.nx._adj == nxG._adj

    def test_can_traverse_undirected_graph(self, backend):
        G = Graph(backend=backend())
        nxG = nx.Graph()
        md = dict(k="B")
        G.nx.add_edge("A", "B", **md)
        nxG.add_edge("A", "B", **md)
        assert dict(nx.bfs_successors(G.nx, "A")) == dict(nx.bfs_successors(nxG, "A"))
        G.nx.add_edge("B", "C", **md)
        nxG.add_edge("B", "C", **md)
        assert dict(nx.bfs_successors(G.nx, "A")) == dict(nx.bfs_successors(nxG, "A"))
        G.nx.add_edge("B", "D", **md)
        nxG.add_edge("B", "D", **md)
        assert dict(nx.bfs_successors(G.nx, "A")) == dict(nx.bfs_successors(nxG, "A"))
        assert dict(nx.bfs_successors(G.nx, "C")) == dict(nx.bfs_successors(nxG, "C"))

    def test_can_traverse_directed_graph(self, backend):
        G = Graph(backend=backend(directed=True))
        nxG = nx.DiGraph()
        md = dict(k="B")
        G.nx.add_edge("A", "B", **md)
        nxG.add_edge("A", "B", **md)
        assert dict(nx.bfs_successors(G.nx, "A")) == dict(nx.bfs_successors(nxG, "A"))
        G.nx.add_edge("B", "C", **md)
        nxG.add_edge("B", "C", **md)
        assert dict(nx.bfs_successors(G.nx, "A")) == dict(nx.bfs_successors(nxG, "A"))
        G.nx.add_edge("B", "D", **md)
        nxG.add_edge("B", "D", **md)
        assert dict(nx.bfs_successors(G.nx, "A")) == dict(nx.bfs_successors(nxG, "A"))
        assert dict(nx.bfs_successors(G.nx, "C")) == dict(nx.bfs_successors(nxG, "C"))

    def test_subgraph_isomorphism_undirected(self, backend):
        G = Graph(backend=backend(directed=False))
        nxG = nx.Graph()

        G.nx.add_edge("A", "B")
        nxG.add_edge("A", "B")
        G.nx.add_edge("B", "C")
        nxG.add_edge("B", "C")
        G.nx.add_edge("C", "A")
        nxG.add_edge("C", "A")

        from networkx.algorithms.isomorphism import GraphMatcher

        assert len(
            [i for i in GraphMatcher(G.nx, G.nx).subgraph_monomorphisms_iter()]
        ) == len([i for i in GraphMatcher(nxG, nxG).subgraph_monomorphisms_iter()])

    def test_subgraph_isomorphism_directed(self, backend):
        G = Graph(backend=backend(directed=True))
        nxG = nx.DiGraph()

        G.nx.add_edge("A", "B")
        nxG.add_edge("A", "B")
        G.nx.add_edge("B", "C")
        nxG.add_edge("B", "C")
        G.nx.add_edge("C", "A")
        nxG.add_edge("C", "A")

        from networkx.algorithms.isomorphism import DiGraphMatcher

        assert len(
            [i for i in DiGraphMatcher(G.nx, G.nx).subgraph_monomorphisms_iter()]
        ) == len([i for i in DiGraphMatcher(nxG, nxG).subgraph_monomorphisms_iter()])
