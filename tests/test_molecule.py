import unittest

import numpy

from molml.molecule import BagOfBonds, Connectivity, Autocorrelation
from molml.molecule import CoulombMatrix, EncodedBond, EncodedAngle
from molml.molecule import ConnectivityTree
from molml.constants import UNKNOWN

from .constants import METHANE, BIG, MID, ALL_DATA

METHANE2 = (METHANE[0], 2 * METHANE[1])
ALL_ATOM = numpy.array([[1, 4, 0, 0],
                        [2, 3, 0, 4],
                        [25, 15, 5, 4]])
ALL_ATOM_TREE = numpy.array([
    [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  4,  0,  0,
     0,  0,  0,  0,  0,  0,  0,  0,  0],
    [1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  1,  0,  2,  0,
     0,  0,  0,  0,  1,  1,  0,  0,  2],
    [0,  2,  1,  1,  2,  1,  0,  2,  5,  2,  3,  5,  1,  0,  0, 11,  0,  2,
     2,  1,  1,  3,  0,  0,  2,  2,  0],
])


def assert_close_statistics(array, expected):
    '''
    Compare float arrays by comparing some statistics.
    '''
    value = numpy.array([
                        array.mean(),
                        array.std(),
                        array.min(),
                        array.max(),
                        ])
    numpy.testing.assert_array_almost_equal(value, expected)


class ConnectivityTest(unittest.TestCase):

    def test_fit_atom(self):
        a = Connectivity(depth=1)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_groups, (('C',), ('H',), ('N',), ('O',)))

    def test_fit_atom_separated(self):
        a = Connectivity(depth=1)
        a.fit([METHANE2])
        self.assertEqual(a._base_groups, (('C',), ('H',)))
        self.assertTrue(
            (a.transform([METHANE2]) == numpy.array([[1, 4]])).all())

    def test_fit_bond(self):
        a = Connectivity(depth=2)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_groups,
                         (('C', 'C'), ('C', 'H'), ('C', 'N'), ('C', 'O'),
                          ('H', 'H'), ('H', 'N'), ('H', 'O'), ('O', 'O')))

    def test_fit_angle(self):
        a = Connectivity(depth=3)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_groups,
                         (('C', 'C', 'C'), ('C', 'C', 'H'),
                          ('C', 'C', 'N'), ('C', 'C', 'O'),
                          ('C', 'N', 'C'), ('C', 'N', 'H'),
                          ('C', 'O', 'C'), ('C', 'O', 'H'),
                          ('H', 'C', 'H'), ('H', 'C', 'N'),
                          ('H', 'C', 'O'), ('H', 'N', 'H'),
                          ('N', 'C', 'N'), ('N', 'C', 'O')))

    def test_fit_dihedral(self):
        # This is to test the double order flipping (CCCH vs HCCC)
        a = Connectivity(depth=4)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_groups,
                         (('C', 'C', 'C', 'C'), ('C', 'C', 'C', 'H'),
                          ('C', 'C', 'C', 'N'), ('C', 'C', 'C', 'O'),
                          ('C', 'C', 'N', 'C'), ('C', 'C', 'N', 'H'),
                          ('C', 'C', 'O', 'C'), ('C', 'C', 'O', 'H'),
                          ('H', 'C', 'C', 'H'), ('H', 'C', 'C', 'N'),
                          ('H', 'C', 'C', 'O'), ('H', 'C', 'N', 'C'),
                          ('H', 'C', 'O', 'C'), ('N', 'C', 'C', 'O'),
                          ('N', 'C', 'N', 'C'), ('N', 'C', 'N', 'H'),
                          ('N', 'C', 'O', 'H'), ('O', 'C', 'N', 'C')))

    def test_fit_atom_bond(self):
        # This should be the exact same thing as doing it with
        # use_bond_order=False
        a = Connectivity(depth=1, use_bond_order=True)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_groups, (('C',), ('H',), ('N',), ('O',)))

    def test_fit_bond_bond(self):
        a = Connectivity(depth=2, use_bond_order=True)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_groups,
                         ((('C', 'C', '1'),), (('C', 'C', '2'),),
                          (('C', 'C', '3'),), (('C', 'C', 'Ar'),),
                          (('C', 'H', '1'),), (('C', 'N', '2'),),
                          (('C', 'N', '3'),), (('C', 'N', 'Ar'),),
                          (('C', 'O', '1'),), (('C', 'O', 'Ar'),),
                          (('H', 'H', '1'),), (('H', 'N', '1'),),
                          (('H', 'O', '1'),), (('O', 'O', '1'),)))

    def test_fit_atom_coordination(self):
        a = Connectivity(depth=1, use_coordination=True)
        a.fit(ALL_DATA)
        self.assertEqual(a._base_groups,
                         (('C1',), ('C2',), ('C3',), ('C4',), ('H0',),
                          ('H1',), ('N1',), ('N2',), ('N3',), ('O0',),
                          ('O1',), ('O2',)))

    def test_transform(self):
        a = Connectivity()
        a.fit(ALL_DATA)
        self.assertTrue((a.transform(ALL_DATA) == ALL_ATOM).all())

    def test_small_to_large_transform(self):
        a = Connectivity()
        a.fit([METHANE])
        self.assertTrue((a.transform(ALL_DATA) == ALL_ATOM[:, :2]).all())

    def test_large_to_small_transform(self):
        a = Connectivity()
        a.fit([BIG])
        self.assertTrue((a.transform(ALL_DATA) == ALL_ATOM).all())

    def test_transform_before_fit(self):
        a = Connectivity()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_fit_transform(self):
        a = Connectivity()
        self.assertTrue((a.fit_transform(ALL_DATA) == ALL_ATOM).all())

    def test_unknown(self):
        a = Connectivity(add_unknown=True)
        expected_results = numpy.array([[1,  4, 0],
                                        [2,  3, 4],
                                        [25, 15, 9]])
        a.fit([METHANE])
        self.assertTrue((a.transform(ALL_DATA) == expected_results).all())

    def test_tfidf(self):
        a = Connectivity(do_tfidf=True)
        expected = numpy.array([[0., 0.,  0., 0.],
                                [0., 0., 0., 1.62186043],
                                [0., 0., 5.49306144, 1.62186043]])
        a.fit(ALL_DATA)
        try:
            m = a.transform(ALL_DATA)
            numpy.testing.assert_array_almost_equal(m, expected)
        except AssertionError as e:
            self.fail(e)

    def test_get_labels(self):
        a = Connectivity(depth=2)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('C-H', )
        self.assertEqual(labels, expected)

    def test_get_labels_unknown(self):
        a = Connectivity(depth=2, add_unknown=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('C-H', UNKNOWN)
        self.assertEqual(labels, expected)

    def test_get_labels_coordination(self):
        a = Connectivity(depth=1, use_coordination=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('C4', 'H1')
        self.assertEqual(labels, expected)

    def test_get_labels_bond_order(self):
        a = Connectivity(depth=3, use_bond_order=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('H-C-1_C-H-1', )
        self.assertEqual(labels, expected)


class ConnectivityTreeTest(unittest.TestCase):

    def test_fit_depth_1(self):
        a = ConnectivityTree(depth=1, use_parent_element=False)
        a.fit(ALL_DATA)
        base = ('C', 'H', 'N', 'O')
        self.assertEqual(a._base_groups, tuple(((0, x, 1), ) for x in base))

    def test_fit_depth_1_separated(self):
        a = ConnectivityTree(depth=1)
        a.fit([METHANE2])
        self.assertTrue(
            (a.transform([METHANE2]) == numpy.array([[1, 4]])).all())

    def test_fit_depth_2(self):
        a = ConnectivityTree(depth=2, use_parent_element=False)
        a.fit(ALL_DATA)
        expected = (
            ((0, 'C', 1), (1, 'C', 1)),
            ((0, 'C', 1), (1, 'C', 1), (1, 'H', 1), (1, 'N', 1)),
            ((0, 'C', 1), (1, 'C', 1), (1, 'N', 1), (1, 'O', 1)),
            ((0, 'C', 1), (1, 'C', 1), (1, 'O', 1)),
            ((0, 'C', 1), (1, 'C', 2), (1, 'H', 1)),
            ((0, 'C', 1), (1, 'C', 2), (1, 'O', 1)),
            ((0, 'C', 1), (1, 'H', 3), (1, 'O', 1)), ((0, 'H', 1),),
            ((0, 'H', 1), (1, 'H', 1)),
            ((0, 'H', 1), (1, 'O', 1)),
            ((0, 'N', 1), (1, 'C', 1), (1, 'H', 2)), ((0, 'O', 1),),
            ((0, 'O', 1), (1, 'C', 1), (1, 'H', 1)),
            ((0, 'O', 1), (1, 'O', 1)),
        )
        self.assertEqual(a._base_groups[::2], expected)

    def test_fit_depth_2_parent_element(self):
        a = ConnectivityTree(depth=2, use_parent_element=True)
        a.fit(ALL_DATA)
        expected = (
            ((0, 'Root', 'C', 1), (1, 'C', 'C', 1)),
            ((0, 'Root', 'C', 1), (1, 'C', 'C', 1), (1, 'C', 'H', 1),
             (1, 'C', 'N', 1)),
            ((0, 'Root', 'C', 1), (1, 'C', 'C', 1), (1, 'C', 'N', 1),
             (1, 'C', 'O', 1)),
            ((0, 'Root', 'C', 1), (1, 'C', 'C', 1), (1, 'C', 'O', 1)),
            ((0, 'Root', 'C', 1), (1, 'C', 'C', 2), (1, 'C', 'H', 1)),
            ((0, 'Root', 'C', 1), (1, 'C', 'C', 2), (1, 'C', 'O', 1)),
            ((0, 'Root', 'C', 1), (1, 'C', 'H', 3), (1, 'C', 'O', 1)),
            ((0, 'Root', 'H', 1),),
            ((0, 'Root', 'H', 1), (1, 'H', 'H', 1)),
            ((0, 'Root', 'H', 1), (1, 'H', 'O', 1)),
            ((0, 'Root', 'N', 1), (1, 'N', 'C', 1), (1, 'N', 'H', 2)),
            ((0, 'Root', 'O', 1),),
            ((0, 'Root', 'O', 1), (1, 'O', 'C', 1), (1, 'O', 'H', 1)),
            ((0, 'Root', 'O', 1), (1, 'O', 'O', 1)),
        )
        self.assertEqual(a._base_groups[::2], expected)

    def test_fit_depth_2_parent_element_bond_order(self):
        a = ConnectivityTree(depth=2, use_parent_element=True,
                             use_bond_order=True)
        a.fit(ALL_DATA)
        expected = (
            ((1, 'C_1_C', 1), (1, 'C_2_C', 2)),
            ((1, 'C_1_H', 1), (1, 'C_Ar_C', 1), (1, 'C_Ar_N', 1)),
            ((1, 'C_1_H', 3), (1, 'C_1_O', 1)),
            ((1, 'C_1_O', 1), (1, 'C_2_C', 2)),
            ((1, 'C_2_C', 1), (1, 'C_3_C', 1)),
            ((1, 'C_2_C', 1), (1, 'C_Ar_C', 1), (1, 'C_Ar_N', 1)),
            ((1, 'C_2_N', 1), (1, 'C_Ar_C', 1), (1, 'C_Ar_N', 1)),
            ((1, 'C_Ar_C', 1), (1, 'C_Ar_N', 1), (1, 'C_Ar_O', 1)),
            ((1, 'H_1_C', 1),),
            ((1, 'H_1_N', 1),),
            ((1, 'N_1_H', 2), (1, 'N_2_C', 1)),
            ((1, 'N_Ar_C', 2),),
            ((1, 'O_1_C', 1), (1, 'O_Ar_C', 1)),
            ((1, 'O_1_H', 1), (1, 'O_Ar_C', 1)),
        )
        self.assertEqual(a._base_groups[::2], expected)

    def test_fit_depth_3(self):
        a = ConnectivityTree(depth=3, use_parent_element=False,
                             preserve_paths=False)
        a.fit(ALL_DATA)
        expected = (
            ((0, 'C', 1), (1, 'C', 1), (1, 'H', 1), (1, 'N', 1), (2, 'C', 3)),
            ((0, 'C', 1), (1, 'C', 1), (1, 'N', 2), (2, 'C', 3), (2, 'H', 2)),
            ((0, 'C', 1), (1, 'C', 2), (1, 'H', 1), (2, 'C', 2), (2, 'H', 2)),
            ((0, 'C', 1), (1, 'C', 2), (1, 'O', 1), (2, 'C', 3), (2, 'H', 1),
             (2, 'N', 1)),
            ((0, 'C', 1), (1, 'C', 3), (2, 'C', 2), (2, 'H', 2), (2, 'N', 1)),
            ((0, 'H', 1),),
            ((0, 'H', 1), (1, 'C', 1), (2, 'H', 3)),
            ((0, 'N', 1), (1, 'C', 1), (2, 'C', 1)),
            ((0, 'O', 1), (1, 'C', 1), (2, 'C', 1))
        )
        self.assertEqual(a._base_groups[::5], expected)

    def test_fit_depth_3_preserve_paths(self):
        a = ConnectivityTree(depth=3, use_parent_element=False,
                             preserve_paths=True)
        a.fit(ALL_DATA)
        expected = (
            ((0, -1, 'C', 1), (1, 0, 'C', 1), (1, 0, 'H', 1), (1, 0, 'N', 1),
             (2, 0, 'C', 2), (2, 2, 'C', 1)),
            ((0, -1, 'C', 1), (1, 0, 'C', 1), (1, 0, 'N', 2), (2, 0, 'C', 2),
             (2, 1, 'C', 1), (2, 2, 'H', 2)),
            ((0, -1, 'C', 1), (1, 0, 'C', 2), (1, 0, 'H', 1), (2, 0, 'C', 1),
             (2, 0, 'H', 1), (2, 1, 'N', 1), (2, 1, 'O', 1)),
            ((0, -1, 'C', 1), (1, 0, 'C', 2), (1, 0, 'O', 1), (2, 0, 'C', 1),
             (2, 0, 'H', 1), (2, 1, 'C', 1), (2, 1, 'N', 1), (2, 2, 'C', 1)),
            ((0, -1, 'C', 1), (1, 0, 'C', 3), (2, 0, 'C', 1), (2, 0, 'H', 1),
             (2, 1, 'C', 1), (2, 1, 'O', 1), (2, 2, 'N', 2)),
            ((0, -1, 'C', 1), (1, 0, 'H', 4)),
            ((0, -1, 'H', 1), (1, 0, 'C', 1), (2, 0, 'H', 2), (2, 0, 'O', 1)),
            ((0, -1, 'N', 1), (1, 0, 'C', 1), (1, 0, 'H', 2), (2, 0, 'C', 1),
             (2, 0, 'N', 1)),
            ((0, -1, 'O', 1), (1, 0, 'C', 1), (1, 0, 'H', 1), (2, 0, 'C', 1),
             (2, 0, 'N', 1)),
        )
        self.assertEqual(a._base_groups[::5], expected)

    def test_fit_depth_1_use_bond_order(self):
        # This should be the exact same thing as doing it with
        # use_bond_order=False
        a = ConnectivityTree(depth=1, use_parent_element=False,
                             use_bond_order=True)
        a.fit(ALL_DATA)
        base = ('C', 'H', 'N', 'O')
        self.assertEqual(a._base_groups, tuple(((0, x, 1), ) for x in base))

    def test_fit_depth_2_use_bond_order(self):
        a = ConnectivityTree(depth=2, use_parent_element=False,
                             use_bond_order=True)
        a.fit(ALL_DATA)
        expected = (
            ((1, 'C_1_C', 1), (1, 'C_2_C', 2)),
            ((1, 'C_1_H', 4),),
            ((1, 'C_2_C', 1), (1, 'C_Ar_C', 1), (1, 'C_Ar_N', 1)),
            ((1, 'C_Ar_C', 2), (1, 'C_Ar_O', 1)),
            ((1, 'N_1_H', 2), (1, 'N_2_C', 1)),
            ((1, 'O_1_C', 2),),
        )
        self.assertEqual(a._base_groups[::5], expected)

    def test_fit_depth_1_coordination(self):
        a = ConnectivityTree(depth=1, use_coordination=True)
        a.fit(ALL_DATA)

        bases = ('C1', 'C2', 'C3', 'C4', 'H0', 'H1',
                 'N1', 'N2', 'N3', 'O0', 'O1', 'O2')
        expected = tuple(((0, 'Root', x, 1), ) for x in bases)
        self.assertEqual(a._base_groups, expected)

    def test_sorting_order(self):
        eles = ['A', 'B', 'B', 'B', 'C', 'D', 'B']
        connections = {
            0: {1: '1', 2: '1', 3: '1'},
            1: {0: '1', 4: '1'},
            2: {0: '1', 5: '1'},
            3: {0: '1', 6: '1'},
            4: {1: '1'},
            5: {2: '1'},
            6: {3: '1'},
        }
        a = ConnectivityTree(input_type=('elements', 'connections'), depth=3,
                             preserve_paths=True, use_parent_element=True)
        a.fit([(eles, connections)])
        expected = (
            (0, -1, 'Root', 'A', 1),
            (1, 0, 'A', 'B', 3),
            (2, 0, 'B', 'B', 1),
            (2, 1, 'B', 'C', 1),
            (2, 2, 'B', 'D', 1),
        )
        a_base = [x for x in a._base_groups if x[0][-2] == 'A']
        self.assertEqual(len(a_base), 1)
        self.assertEqual(a_base[0], expected)

    def test_transform(self):
        a = ConnectivityTree()
        a.fit(ALL_DATA)
        self.assertTrue((a.transform(ALL_DATA) == ALL_ATOM).all())

    def test_small_to_large_transform(self):
        a = ConnectivityTree(depth=2)
        a.fit([METHANE])
        idxs = numpy.where(ALL_ATOM_TREE[0] != 0)[0]
        expected = ALL_ATOM_TREE[:, idxs]
        self.assertTrue((a.transform(ALL_DATA) == expected).all())

    def test_large_to_small_transform(self):
        a = ConnectivityTree(depth=2)
        a.fit([BIG])
        idxs = numpy.where(ALL_ATOM_TREE[2] != 0)[0]
        expected = ALL_ATOM_TREE[:, idxs]
        self.assertTrue((a.transform(ALL_DATA) == expected).all())

    def test_transform_before_fit(self):
        a = ConnectivityTree()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_fit_transform(self):
        a = ConnectivityTree(depth=2)
        self.assertTrue((a.fit_transform(ALL_DATA) == ALL_ATOM_TREE).all())

    def test_unknown(self):
        a = ConnectivityTree(add_unknown=True)
        expected_results = numpy.array([[1,  4, 0],
                                        [2,  3, 4],
                                        [25, 15, 9]])
        a.fit([METHANE])
        self.assertTrue((a.transform(ALL_DATA) == expected_results).all())

    def test_tfidf(self):
        a = ConnectivityTree(do_tfidf=True)
        expected = numpy.array([[0., 0.,  0., 0.],
                                [0., 0., 0., 1.62186043],
                                [0., 0., 5.49306144, 1.62186043]])
        a.fit(ALL_DATA)
        try:
            m = a.transform(ALL_DATA)
            numpy.testing.assert_array_almost_equal(m, expected)
        except AssertionError as e:
            self.fail(e)

    def test_get_labels(self):
        a = ConnectivityTree(depth=2)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('0-Root-C-1__1-C-H-4', '0-Root-H-1__1-H-C-1')
        self.assertEqual(labels, expected)

    def test_get_labels_unknown(self):
        a = ConnectivityTree(depth=2, add_unknown=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('0-Root-C-1__1-C-H-4', '0-Root-H-1__1-H-C-1', UNKNOWN)
        self.assertEqual(labels, expected)

    def test_get_labels_coordination(self):
        a = ConnectivityTree(depth=1, use_coordination=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('0-Root-C4-1', '0-Root-H1-1')
        self.assertEqual(labels, expected)

    def test_get_labels_bond_order(self):
        a = ConnectivityTree(depth=3, use_bond_order=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('1-C_1_H-4', '1-H_1_C-1__2-C_1_H-3')
        self.assertEqual(labels, expected)


class AutocorrelationTest(unittest.TestCase):

    def test_depths_properties(self):
        a = Autocorrelation(depths=[1, 2], properties=['I', 'Z'])
        a.fit([METHANE])
        self.assertTrue(
            (a.transform([METHANE]) == numpy.array([[8, 12, 48, 12]])).all())

    def test_fit_atom_separated(self):
        a = Autocorrelation(depths=[0, 1], properties=['I', 'Z'])
        a.fit([METHANE2])
        self.assertTrue(
            (a.transform([METHANE2]) == numpy.array([[5, 0, 40, 0]])).all())

    def test_default_depths(self):
        a = Autocorrelation(properties=['I'])
        a.fit(ALL_DATA)
        expected = numpy.array([
            [5, 8, 12, 0],
            [9, 8, 2, 0],
            [49, 104, 156, 190]
        ])
        self.assertTrue((a.transform(ALL_DATA) == expected).all())

    def test_wide_depths(self):
        a = Autocorrelation(depths=[-1, 1, 4, 10, 100], properties=['I'])
        a.fit(ALL_DATA)
        expected = numpy.array([
            [0, 8, 0, 0, 0],
            [0, 8, 0, 0, 0],
            [0, 104, 216, 166, 0]
        ])
        self.assertTrue((a.transform(ALL_DATA) == expected).all())

    def test_properties(self):
        a = Autocorrelation(depths=[0])
        a.fit(ALL_DATA)
        expected = numpy.array([
            [20., 25.8625, 5., 2.1625, 40.],
            [10., 74.8594, 9., 4.4571, 331.],
            [260., 328.7049, 49., 28.1326, 1416.]
        ])
        try:
            m = a.transform(ALL_DATA)
            numpy.testing.assert_array_almost_equal(m, expected)
        except AssertionError as e:
            self.fail(e)

    def test_property_function(self):
        a = Autocorrelation(depths=[1],
                            properties=[lambda data:
                                        [2 for x in data.numbers]])
        a.fit(ALL_DATA)
        expected = numpy.array([
            [32],
            [32],
            [416],
        ])
        self.assertTrue((a.transform(ALL_DATA) == expected).all())

    def test_both_property(self):
        a = Autocorrelation(depths=[1],
                            properties=['I',
                                        lambda data:
                                        [2 for x in data.numbers]])
        a.fit(ALL_DATA)
        expected = numpy.array([
            [32, 8],
            [32, 8],
            [416, 104],
        ])
        self.assertTrue((a.transform(ALL_DATA) == expected).all())

    def test_transform(self):
        a = Autocorrelation(depths=[1], properties=['I'])
        a.fit(ALL_DATA)
        expected = numpy.array([
            [8],
            [8],
            [104],
        ])
        self.assertTrue((a.transform(ALL_DATA) == expected).all())

    def test_fit_transform(self):
        a = Autocorrelation(depths=[1], properties=['I'])
        expected = numpy.array([
            [8],
            [8],
            [104],
        ])
        self.assertTrue((a.fit_transform(ALL_DATA) == expected).all())

    def test_get_labels(self):
        a = Autocorrelation(depths=[1, 2], properties=['I', 'EN'])
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = (
            'EN_1', 'EN_2',
            'I_1', 'I_2',
        )
        self.assertEqual(labels, expected)


class EncodedBondTest(unittest.TestCase):

    def test_fit(self):
        a = EncodedBond()
        a.fit(ALL_DATA)
        self.assertEqual(a._element_pairs,
                         (('C', 'C'), ('C', 'H'), ('C', 'N'), ('C', 'O'),
                          ('H', 'H'), ('H', 'N'), ('H', 'O'), ('N', 'N'),
                          ('N', 'O'), ('O', 'O')))

    def test_transform(self):
        a = EncodedBond()
        a.fit([METHANE])
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.042672,  # mean
            0.246663,  # std
            0.,  # min
            2.392207,  # max
        ])
        try:
            m = a.transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_large_to_small_transform(self):
        a = EncodedBond()
        a.fit([MID])
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.014224,  # mean
            0.143824,  # std
            0.,  # min
            2.392207,  # max
        ])
        try:
            m = a.transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = EncodedBond()
        a.fit([METHANE])
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            9.207308e-001,  # mean
            1.062388e+000,  # std
            0.,  # min
            5.023670e+000,  # max
        ])
        try:
            m = a.transform([BIG])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_fit_transform(self):
        a = EncodedBond()
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.042672,  # mean
            0.246663,  # std
            0.,  # min
            2.392207,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = EncodedBond()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_smoothing_function(self):
        a = EncodedBond(smoothing="norm_cdf")

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            3.859534e+000,  # mean
            2.182923e+000,  # std
            0.,  # min
            6.000000e+000,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_smoothing_function_error(self):
        a = EncodedBond(smoothing="not valid")

        with self.assertRaises(KeyError):
            a.fit_transform([METHANE])

    def test_max_depth_neg(self):
        a = EncodedBond(max_depth=-1)
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.503237244954,  # mean
            0.857850829564,  # std
            0.,  # min
            7.15861023,  # max
        ])
        try:
            m = a.fit_transform([BIG])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_max_depth_1(self):
        a = EncodedBond(max_depth=1)

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.0443793,  # mean
            0.33766942,  # std
            0.,  # min
            5.76559336,  # max
        ])
        try:
            m = a.fit_transform([BIG])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_max_depth_3(self):
        a = EncodedBond(max_depth=3)

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.192026,  # mean
            0.63276,  # std
            0.,  # min
            7.15861023,  # max
        ])
        try:
            m = a.fit_transform([BIG])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_spacing_inverse(self):
        a = EncodedBond(spacing="inverse")

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.051207,  # mean
            0.269248,  # std
            0.,  # min
            2.387995,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_spacing_log(self):
        a = EncodedBond(spacing="log")

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.072768,  # mean
            0.318508,  # std
            0.,  # min
            2.339376,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_spacing_invalid(self):
        a = EncodedBond(spacing="not valid")

        with self.assertRaises(KeyError):
            a.fit_transform([METHANE])

    def test_form_element(self):
        a = EncodedBond(form=1)

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.085345,  # mean
            0.452595,  # std
            0.,  # min
            4.784414,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            self.assertEqual(m.shape, (1, 200))
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_form_0(self):
        a = EncodedBond(form=0)

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.085345,  # mean
            0.343574,  # std
            0.,  # min
            2.392207,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            self.assertEqual(m.shape, (1, 100))
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_add_unknown(self):
        a = EncodedBond(add_unknown=True)
        a.fit([METHANE])

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.09105,  # mean
            0.231761,  # std
            0.,  # min
            1.869012,  # max
        ])
        try:
            m = a.transform([MID])
            self.assertEqual(m.shape, (1, 300))
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_get_labels(self):
        a = EncodedBond(segments=2, start=0., end=1.)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = (
            'C-H_0.0', 'C-H_1.0',
            'H-H_0.0', 'H-H_1.0',
        )
        self.assertEqual(labels, expected)


class EncodedAngleTest(unittest.TestCase):

    def test_fit(self):
        a = EncodedAngle()
        a.fit(ALL_DATA)
        expected = (('C', 'C', 'C'), ('C', 'C', 'H'), ('C', 'C', 'N'),
                    ('C', 'C', 'O'), ('C', 'H', 'C'), ('C', 'H', 'H'),
                    ('C', 'H', 'N'), ('C', 'H', 'O'), ('C', 'N', 'C'),
                    ('C', 'N', 'H'), ('C', 'N', 'N'), ('C', 'N', 'O'),
                    ('C', 'O', 'C'), ('C', 'O', 'H'), ('C', 'O', 'N'),
                    ('C', 'O', 'O'), ('H', 'C', 'H'), ('H', 'C', 'N'),
                    ('H', 'C', 'O'), ('H', 'H', 'H'), ('H', 'H', 'N'),
                    ('H', 'H', 'O'), ('H', 'N', 'H'), ('H', 'N', 'N'),
                    ('H', 'N', 'O'), ('H', 'O', 'H'), ('H', 'O', 'N'),
                    ('H', 'O', 'O'), ('N', 'C', 'N'), ('N', 'C', 'O'),
                    ('N', 'H', 'N'), ('N', 'H', 'O'), ('N', 'N', 'N'),
                    ('N', 'N', 'O'), ('N', 'O', 'N'), ('N', 'O', 'O'),
                    ('O', 'C', 'O'), ('O', 'H', 'O'), ('O', 'N', 'O'),
                    ('O', 'O', 'O'))
        self.assertEqual(a._groups, expected)

    def test_transform(self):
        a = EncodedAngle()
        a.fit([METHANE])
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.116708,  # mean
            0.450738,  # std
            0.,  # min
            3.043729,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_large_to_small_transform(self):
        a = EncodedAngle()
        a.fit([MID])
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.025935,  # mean
            0.21795,  # std
            0.,  # min
            3.043729,  # max
        ])
        try:
            m = a.transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = EncodedAngle()
        a.fit([METHANE])
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.018603,  # mean
            0.130329,  # std
            0.,  # min
            1.568823,  # max
        ])
        try:
            m = a.transform([MID])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_fit_transform(self):
        a = EncodedAngle()
        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.116708,  # mean
            0.450738,  # std
            0.,  # min
            3.043729,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = EncodedAngle()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_smoothing_function(self):
        a = EncodedAngle(smoothing="norm_cdf")

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            1.5891686,  # mean
            2.5907034,  # std
            0.,         # min
            9.8982443,  # max
        ])
        try:
            m = a.fit_transform([METHANE])
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_smoothing_function_error(self):
        a = EncodedAngle(smoothing="not valid")

        with self.assertRaises(KeyError):
            a.fit_transform([METHANE])

    def test_max_depth(self):
        a = EncodedAngle(max_depth=3)
        # This is a cheap test to prevent needing all the values here
        data = (
            #       mean          std     min      max
            (-1, [0.0325158765862, 0.132101907024, 0.0, 2.01566683797]),
            (1, [0.00491078348799, 0.0463273875823, 0.0, 0.694568644823]),
            (3, [0.0063668265711, 0.0513782485995, 0.0, 0.694568644823]),

        )
        for max_depth, expected in data:
            a = EncodedAngle(max_depth=max_depth)
            expected_results = numpy.array(expected)
            try:
                m = a.fit_transform([MID])
                assert_close_statistics(m, expected_results)
            except AssertionError as e:
                self.fail(e)

    def test_form(self):
        data = (
            #    mean         std   min     max
            (2, [0.155611, 0.581838, 0., 4.395692], 120),
            (1, [0.233417, 0.699744, 0., 4.395692], 80),
            (0, [4.668338e-001, 1.090704e+000, 0., 5.747656e+000], 40),
        )
        for form, expected, size in data:
            a = EncodedAngle(form=form)
            expected_results = numpy.array(expected)
            try:
                m = a.fit_transform([METHANE])
                self.assertEqual(m.shape, (1, size))
                assert_close_statistics(m, expected_results)
            except AssertionError as e:
                self.fail(e)

    def test_add_unknown(self):
        a = EncodedAngle(add_unknown=True)
        a.fit([METHANE])

        # This is a cheap test to prevent needing all the values here
        expected_results = numpy.array([
            0.117057,  # mean
            0.510819,  # std
            0.,  # min
            6.343512,  # max
        ])
        try:
            m = a.transform([MID])
            self.assertEqual(m.shape, (1, 200))
            assert_close_statistics(m, expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_get_labels(self):
        a = EncodedAngle(segments=2)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = (
            'C-H-C_0.0', 'C-H-C_3.14159',
            'C-H-H_0.0', 'C-H-H_3.14159',
            'H-C-H_0.0', 'H-C-H_3.14159',
            'H-H-H_0.0', 'H-H-H_3.14159',
        )
        self.assertEqual(labels, expected)


class CoulombMatrixTest(unittest.TestCase):

    def test_fit(self):
        a = CoulombMatrix()
        a.fit(ALL_DATA)
        self.assertEqual(a._max_size, 49)

    def test_transform(self):
        a = CoulombMatrix()
        a.fit([METHANE])
        expected_results = numpy.array([
            [36.8581052,   5.49459021,   5.49462885,   5.4945,
                5.49031286,   5.49459021,   0.5,   0.56071947,
                0.56071656,   0.56064037,   5.49462885,   0.56071947,
                0.5,   0.56071752,   0.56064089,   5.4945,
                0.56071656,   0.56071752,   0.5,   0.56063783,
                5.49031286,   0.56064037,   0.56064089,   0.56063783,
                0.5]])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = CoulombMatrix()
        a.fit([METHANE])
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_small_to_large_transform_drop_values(self):
        a = CoulombMatrix(drop_values=True)
        a.fit([METHANE])
        a.transform(ALL_DATA)
        self.assertEqual(a.transform(ALL_DATA).shape, (3, 25))

    def test_large_to_small_transform(self):
        a = CoulombMatrix()
        a.fit([MID])

        expected_results = numpy.array([
            [36.8581052,   5.49459021,   5.49462885,   5.4945,
             5.49031286,   0.,   0.,   0.,
             0.,   5.49459021,   0.5,   0.56071947,
             0.56071656,   0.56064037,   0.,   0.,
             0.,   0.,   5.49462885,   0.56071947,
             0.5,   0.56071752,   0.56064089,   0.,
             0.,   0.,   0.,   5.4945,
             0.56071656,   0.56071752,   0.5,   0.56063783,
             0.,   0.,   0.,   0.,
             5.49031286,   0.56064037,   0.56064089,   0.56063783,
             0.5] + [0.0] * 40
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = CoulombMatrix()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_fit_transform(self):
        a = CoulombMatrix()
        expected_results = numpy.array([
            [36.8581052,   5.49459021,   5.49462885,   5.4945,
                5.49031286,   5.49459021,   0.5,   0.56071947,
                0.56071656,   0.56064037,   5.49462885,   0.56071947,
                0.5,   0.56071752,   0.56064089,   5.4945,
                0.56071656,   0.56071752,   0.5,   0.56063783,
                5.49031286,   0.56064037,   0.56064089,   0.56063783,
                0.5]])
        try:
            numpy.testing.assert_array_almost_equal(
                a.fit_transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_sort(self):
        a = CoulombMatrix(sort=True)
        b = CoulombMatrix()

        res_a = a.fit_transform([MID])
        res_b = b.fit_transform([MID])
        self.assertFalse(numpy.allclose(res_a, res_b))
        expected_results = numpy.array([73.51669472, 45.84796673, 20.4393443,
                                        18.51709592, 34.38200956, 19.92342035,
                                        1.71317156, 1.39374152, 1.20676731])

        try:
            numpy.testing.assert_array_almost_equal(
                res_a[0, :9],
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_eigen(self):
        a = CoulombMatrix(eigen=True)

        expected_results = numpy.array([
                                        40.04619974,
                                        -0.06059994,
                                        -0.06071616,
                                        -0.06071957,
                                        -1.00605888,
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.fit_transform([METHANE])[0],
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_only_lower_triangle(self):
        a = CoulombMatrix(only_lower_triangle=True)
        expected_results = numpy.array([36.858105, 5.49459, 0.5, 5.494629,
                                        0.560719, 0.5, 5.4945, 0.560717,
                                        0.560718, 0.5, 5.490313, 0.56064,
                                        0.560641, 0.560638, 0.5])
        try:
            numpy.testing.assert_array_almost_equal(
                a.fit_transform([METHANE])[0],
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_get_labels(self):
        a = CoulombMatrix()
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = (
            'coul-0-0', 'coul-0-1', 'coul-0-2', 'coul-0-3', 'coul-0-4',
            'coul-1-0', 'coul-1-1', 'coul-1-2', 'coul-1-3', 'coul-1-4',
            'coul-2-0', 'coul-2-1', 'coul-2-2', 'coul-2-3', 'coul-2-4',
            'coul-3-0', 'coul-3-1', 'coul-3-2', 'coul-3-3', 'coul-3-4',
            'coul-4-0', 'coul-4-1', 'coul-4-2', 'coul-4-3', 'coul-4-4',
        )
        self.assertEqual(labels, expected)

    def test_get_labels_eigen(self):
        a = CoulombMatrix(eigen=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = ('coul-0', 'coul-1', 'coul-2', 'coul-3', 'coul-4')
        self.assertEqual(labels, expected)

    def test_get_labels_lower_triangle(self):
        a = CoulombMatrix(only_lower_triangle=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = (
            'coul-0-0',
            'coul-1-0', 'coul-1-1',
            'coul-2-0', 'coul-2-1', 'coul-2-2',
            'coul-3-0', 'coul-3-1', 'coul-3-2', 'coul-3-3',
            'coul-4-0', 'coul-4-1', 'coul-4-2', 'coul-4-3', 'coul-4-4',
        )
        self.assertEqual(labels, expected)


class BagOfBondsTest(unittest.TestCase):

    def test_fit(self):
        a = BagOfBonds()
        a.fit([METHANE])
        expected_results = (
            (('C', 'H'), 4),
            (('H', 'H'), 6),
        )
        self.assertEqual(a._bag_sizes, expected_results)

    def test_fit_multi_mol(self):
        a = BagOfBonds()
        a.fit(ALL_DATA)
        expected_results = (
            (('C', 'C'), 300),
            (('C', 'H'), 375),
            (('C', 'N'), 125),
            (('C', 'O'), 100),
            (('H', 'H'), 105),
            (('H', 'N'), 75),
            (('H', 'O'), 60),
            (('N', 'N'), 10),
            (('N', 'O'), 20),
            (('O', 'O'), 6),
        )
        self.assertEqual(a._bag_sizes, expected_results)

    def test_transform(self):
        a = BagOfBonds()
        a.fit([METHANE])
        expected_results = numpy.array([
            [5.49462885, 5.49459021, 5.4945, 5.49031286, 0.56071947,
             0.56071752, 0.56071656, 0.56064089, 0.56064037, 0.56063783]
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = BagOfBonds()
        a.fit([METHANE])
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_small_to_large_transform_drop_values(self):
        a = BagOfBonds(drop_values=True)
        a.fit([METHANE])
        self.assertEqual(a.transform(ALL_DATA).shape, (3, 10))

    def test_add_atoms(self):
        a = BagOfBonds(add_atoms=True)
        a.fit([METHANE])
        expected_results = numpy.array([[
            36.8581052, 5.49462885, 5.49459021, 5.4945, 5.49031286, 0.5,
            0.5, 0.5, 0.5, 0.56071947, 0.56071752, 0.56071656, 0.56064089,
            0.56064037, 0.56063783]])
        try:

            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_large_to_small_transform(self):
        a = BagOfBonds()
        a.fit([BIG])

        expected_results = numpy.array([
            [0.0] * 300 +
            [5.494628848219048, 5.494590213211275, 5.494499999706413,
             5.49031286145183] +
            [0.0] * 596 +
            [0.5607194714171738, 0.5607175240809282, 0.5607165613824526,
             0.5606408892793993, 0.5606403708987712, 0.560637829974531] +
            [0.0] * 270
        ])
        try:
            numpy.testing.assert_array_almost_equal(
                a.transform([METHANE]),
                expected_results)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = BagOfBonds()
        with self.assertRaises(ValueError):
            a.transform(ALL_DATA)

    def test_get_labels(self):
        a = BagOfBonds()
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = (
            'C-H_0', 'C-H_1', 'C-H_2', 'C-H_3',
            'H-H_0', 'H-H_1', 'H-H_2',
            'H-H_3', 'H-H_4', 'H-H_5',
        )
        self.assertEqual(labels, expected)

    def test_get_labels_add_atoms(self):
        a = BagOfBonds(add_atoms=True)
        X = a.fit_transform([METHANE])
        labels = a.get_labels()
        self.assertEqual(X.shape[1], len(labels))
        expected = (
            'C_0',
            'C-H_0', 'C-H_1', 'C-H_2', 'C-H_3',
            'H_0', 'H_1', 'H_2', 'H_3',
            'H-H_0', 'H-H_1', 'H-H_2',
            'H-H_3', 'H-H_4', 'H-H_5',
        )
        self.assertEqual(labels, expected)


if __name__ == '__main__':
    unittest.main()
