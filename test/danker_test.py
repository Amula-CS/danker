#!/usr/bin/env python3

"""
danker test cases
"""
import unittest
import networkx as nx
import numpy as np
import lib.danker

class DankerTest(unittest.TestCase):
    """
    danker test cases
    """

    def _compare(self, netx, danker):
        """
        Helper method to compare danker and NetworkX outputs.
        """
        self.assertEqual(len(netx), len(danker))
        self.assertEqual(len(netx.keys() - danker.keys()), 0)
        self.assertEqual(len(danker.keys() - netx.keys()), 0)
        result = [[], []]
        for i in netx.keys():
            result[0].append(netx.get(i))
            result[1].append(danker.get(i)[1])
        res = np.array(result)
        print("Pearson correlation:")
        print(np.corrcoef(res[0], res[1]))
        self.assertAlmostEqual(np.corrcoef(res[0], res[1])[0][1], 1, places=6)

    def test_assert_left_sort(self):
        """
        Test if assert for left sort works (test with right sorted file)
        """
        link_file_right = "./test/graphs/test.links.right"
        with self.assertRaises(AssertionError):
            lib.danker.init(link_file_right, 0.1, False)

    def test_assert_right_sort(self):
        """
        Test if assert for right sort works (test with left sorted file)
        """
        link_file = "./test/graphs/test.links"
        danker_graph = lib.danker.init(link_file, 0.1, True)
        with self.assertRaises(AssertionError):
            lib.danker.danker_smallmem(danker_graph, link_file, 50, 0.85, 0.1)

    def test_general(self):
        """
        Test with a very small graph and comparision between danker and NetworkX.
        """
        link_file = "./test/graphs/test.links"
        link_file_right = "./test/graphs/test.links.right"
        nx_graph = nx.read_edgelist(link_file, create_using=nx.DiGraph, nodetype=str,
                                    delimiter='\t')
        nx_pr = nx.pagerank(nx_graph, tol=1e-8)
        danker_graph = lib.danker.init(link_file, 0.1, False)
        danker_pr_big = lib.danker.danker_bigmem(danker_graph, 50, 0.85)
        self._compare(nx_pr, danker_pr_big)
        danker_pr_small = lib.danker.danker_smallmem(danker_graph, link_file_right, 50, 0.85, 0.1)
        self._compare(nx_pr, danker_pr_small)

    def test_bar(self):
        """
        Test with a small graph (Bavarian Wikilinks) and comparision between danker and NetworkX.
        """
        link_file = "./test/graphs/bar-20190301.links"
        link_file_right = "./test/graphs/bar-20190301.links.right"
        nx_graph = nx.read_edgelist(link_file, create_using=nx.DiGraph, nodetype=int,
                                    delimiter='\t')
        nx_pr = nx.pagerank(nx_graph, tol=1e-8)
        danker_graph = lib.danker.init(link_file, 0.1, False)
        danker_pr_big = lib.danker.danker_bigmem(danker_graph, 50, 0.85)
        self._compare(nx_pr, danker_pr_big)
        danker_pr_small = lib.danker.danker_smallmem(danker_graph, link_file_right, 50, 0.85, 0.1)
        self._compare(nx_pr, danker_pr_small)

if __name__ == '__main__':
    unittest.main()
