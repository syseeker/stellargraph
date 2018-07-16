# -*- coding: utf-8 -*-
#
# Copyright 2017-2018 Data61, CSIRO
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import networkx as nx
from stellar.data.explorer import SampledBreadthFirstWalk


def create_test_graph():
    """
    Creates a simple graph for testing the BreadthFirstWalk class. The node ids are string or integers.

    :return: A simple graph with 13 nodes and 24 edges (including self loops for all but two of the nodes) in
    networkx format.
    """
    g = nx.Graph()
    edges = [
        ("0", 1),
        ("0", 2),
        (1, 3),
        (1, 4),
        (3, 6),
        (4, 7),
        (4, 8),
        (2, 5),
        (5, 9),
        (5, 10),
        ("0", "0"),
        (1, 1),
        (3, 3),
        (6, 6),
        (4, 4),
        (7, 7),
        (8, 8),
        (2, 2),
        (5, 5),
        (9, 9),
        (
            "self loner",
            "self loner",
        ),  # node that is not connected with any other nodes but has self loop
    ]

    g.add_edges_from(edges)
    g.add_node(
        "loner"
    )  # node that is not connected to any other nodes and not having a self loop

    return g


def expected_bfw_size(n_size):
    """
    Calculates the number of nodes generated by a single BFW for a single root node.
    :param n_size: <list> The number of neighbours at each depth level
    :return: The size of the list returned by a single BFW on a single root node
    """
    total = []
    for i, d in enumerate(n_size):
        if i == 0:
            total.append(d)
        else:
            total.append(total[-1] * d)
    return sum(total) + 1  # add the root node


class TestBreadthFirstWalk(object):
    def test_parameter_checking(self):
        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["0", 1]
        n = 1
        n_size = [1]

        with pytest.raises(ValueError):
            # nodes should be a list of node ids even for a single node
            bfw.run(nodes=None, n=n, n_size=n_size)
            bfw.run(nodes=0, n=n, n_size=n_size)
            # only list is acceptable type for nodes
            bfw.run(nodes=(1, 2), n=n, n_size=n_size)
            # n has to be positive integer
            bfw.run(nodes=nodes, n=-1, n_size=n_size)
            bfw.run(nodes=nodes, n=10.1, n_size=n_size)
            bfw.run(nodes=nodes, n=0, n_size=n_size)
            # n_size has to be list of positive integers
            bfw.run(nodes=nodes, n=n, n_size=0)
            bfw.run(nodes=nodes, n=n, n_size=[-5])
            bfw.run(nodes=nodes, n=-1, n_size=[2.4])
            bfw.run(nodes=nodes, n=n, n_size=(1, 2))
            # seed must be positive integer or 0
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed=-1235)
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed=10.987665)
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed=-982.4746)
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed="don't be random")

        # If no root nodes are given, an empty list is returned which is not an error but I thought this method
        # is the best for checking this behaviour.
        nodes = []
        subgraph = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraph) == 0

    def test_walk_generation_single_root_node_loner(self):
        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["loner"]
        n = 1
        n_size = [0]

        # all should raise ValueError
        with pytest.raises(ValueError):
            subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)

            n_size = [1]
            subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)

            n_size = [2, 2]
            subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)

            n_size = [3, 2]
            subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)

    def test_walk_generation_single_root_node_self_loner(self):
        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["self loner"]
        n = 1

        n_size = [0]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

        n = 3
        n_size = [0]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

    def test_walk_generation_single_root_node(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["0"]
        n = 1
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)

        # subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        # assert len(subgraphs[0]) == 2

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [1, 1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

    def test_walk_generation_many_root_nodes(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["0", 2]
        n = 1
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for i, subgraph in enumerate(subgraphs):
            assert len(subgraph) == 1
            assert subgraph[0] == nodes[i]  # should equal the root node

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [1, 1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2, 3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

    def test_walk_generation_number_of_walks_per_root_nodes(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = [1]
        n = 2
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for i, subgraph in enumerate(subgraphs):
            assert len(subgraph) == expected_bfw_size(n_size=n_size)
            assert subgraph[0] == nodes[0]  # should equal the root node

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        #############################################################
        nodes = [1, 5]
        n_size = [1]
        n = 2

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        #############################################################
        nodes = [1, 5]
        n_size = [2, 2]
        n = 3

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [4, 4]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

    def test_fixed_random_seed(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        w0 = bfw.run(nodes=[1], n=1, n_size=[7], seed=42)
        w1 = bfw.run(nodes=[1], n=1, n_size=[7], seed=1010)

        assert len(w0) == len(w1)
        assert w0 != w1

        w0 = bfw.run(nodes=[1], n=1, n_size=[7], seed=42)
        w1 = bfw.run(nodes=[1], n=1, n_size=[7], seed=42)

        assert len(w0) == len(w1)
        assert w0 == w1

        w0 = bfw.run(nodes=[1], n=5, n_size=[12], seed=101)
        w1 = bfw.run(nodes=[1], n=5, n_size=[12], seed=101)

        assert len(w0) == len(w1)
        assert w0 == w1

        w0 = bfw.run(nodes=[9, "self loner"], n=1, n_size=[12], seed=101)
        w1 = bfw.run(nodes=[9, "self loner"], n=1, n_size=[12], seed=101)

        assert len(w0) == len(w1)
        assert w0 == w1

        w0 = bfw.run(nodes=[1, "self loner", 4], n=5, n_size=[12], seed=101)
        w1 = bfw.run(nodes=[1, "self loner", 4], n=5, n_size=[12], seed=101)

        assert len(w0) == len(w1)
        assert w0 == w1
