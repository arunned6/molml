import unittest
import os

import numpy

from molml.molecule import Connectivity
from molml.crystal import GenerallizedCrystal
from molml.crystal import EwaldSumMatrix, SineMatrix


DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
ELEMENTS = ['C', 'H', 'H', 'H', 'H']
NUMBERS = [6, 1, 1, 1, 1]
COORDS = [
    [0.99826008, -0.00246000, -0.00436000],
    [2.09021016, -0.00243000, 0.00414000],
    [0.63379005, 1.02686007, 0.00414000],
    [0.62704006, -0.52773003, 0.87811010],
    [0.64136006, -0.50747003, -0.90540005],
]

H_ELES = ['H']
H_NUMS = [1]
H_COORDS = numpy.array([[0.0, 0.0, 0.0]])
H_UNIT = numpy.array([
    [2., .5, 0.],
    [.25, 1., 0.],
    [0., .3, 1.],
])
H_INPUT = ("elements", "coords", "unit_cell")
H = (H_ELES, H_COORDS, H_UNIT)


H2_ELES = ['H', 'H']
H2_NUMS = [1, 1]
H2_COORDS = numpy.array([
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
])
H2_CONNS = {
    0: {1: '1'},
    1: {0: '1'},
}
H2_UNIT = numpy.array([
    [2., .5, 0.],
    [.25, 1., 0.],
    [0., .3, 1.],
])


class GenerallizedCrystalTest(unittest.TestCase):
    def test_fit(self):
        t = Connectivity(input_type=H_INPUT)
        a = GenerallizedCrystal(transformer=t, radius=2.5)
        a.fit([H])
        self.assertEqual(a.transformer._base_chains, {('H', )})

    def test_transform(self):
        t = Connectivity(input_type=H_INPUT)
        a = GenerallizedCrystal(transformer=t, radius=2.5)
        a.fit([H])
        res = a.transform([H])
        self.assertEqual(res, numpy.array([[37]]))

    def test_transform_before_fit(self):
        t = Connectivity(input_type=H_INPUT)
        a = GenerallizedCrystal(transformer=t, radius=2.5)
        with self.assertRaises(ValueError):
            a.transform([H])

    def test_fit_transform(self):
        t = Connectivity(input_type=H_INPUT)
        a = GenerallizedCrystal(transformer=t, radius=2.5)
        res = a.fit_transform([H])
        self.assertEqual(res, numpy.array([[37]]))

    def test_radius_and_units(self):
        t = Connectivity(input_type=H_INPUT)
        with self.assertRaises(ValueError):
            GenerallizedCrystal(transformer=t, radius=2.5, units=2)


class EwaldSumMatrixCrystalTest(unittest.TestCase):
    def test_fit(self):
        a = EwaldSumMatrix()
        a.fit([(H2_ELES, H2_COORDS)])
        self.assertEqual(a._max_size, 2)

    def test_transform(self):
        a = EwaldSumMatrix(input_type=H_INPUT)
        a.fit([(H2_ELES, H2_COORDS, H2_UNIT)])
        res = a.transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[-1.68059225, 0.94480435,
                                 0.94480435, -1.68059225]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = EwaldSumMatrix(input_type=H_INPUT)
        a.fit([(H_ELES, H_COORDS, H_UNIT)])
        with self.assertRaises(ValueError):
            a.transform([(H2_ELES, H2_COORDS, H2_UNIT)])

    def test_large_to_small_transform(self):
        a = EwaldSumMatrix(input_type=H_INPUT)
        a.fit([(H2_ELES, H2_COORDS, H2_UNIT)])
        res = a.transform([(H_ELES, H_COORDS, H_UNIT)])
        expected = numpy.array([[-1.944276, 0., 0., 0.]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = EwaldSumMatrix()
        with self.assertRaises(ValueError):
            a.transform([H])

    def test_fit_transform(self):
        a = EwaldSumMatrix(input_type=H_INPUT)
        res = a.fit_transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[-1.68059225, 0.94480435,
                                 0.94480435, -1.68059225]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_sort(self):
        a = EwaldSumMatrix(input_type=H_INPUT, sort=True)
        res = a.fit_transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[-1.68059225, 0.94480435,
                                 0.94480435, -1.68059225]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_eigen(self):
        a = EwaldSumMatrix(input_type=H_INPUT, eigen=True)
        res = a.fit_transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[-0.735788, -2.625397]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)


class SineMatrixTest(unittest.TestCase):
    def test_fit(self):
        a = SineMatrix()
        a.fit([(H2_ELES, H2_COORDS)])
        self.assertEqual(a._max_size, 2)

    def test_transform(self):
        a = SineMatrix(input_type=H_INPUT)
        a.fit([(H2_ELES, H2_COORDS, H2_UNIT)])
        res = a.transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[0.5, 0.475557, 0.475557, 0.5]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_small_to_large_transform(self):
        a = SineMatrix(input_type=H_INPUT)
        a.fit([(H_ELES, H_COORDS, H_UNIT)])
        with self.assertRaises(ValueError):
            a.transform([(H2_ELES, H2_COORDS, H2_UNIT)])

    def test_large_to_small_transform(self):
        a = SineMatrix(input_type=H_INPUT)
        a.fit([(H2_ELES, H2_COORDS, H2_UNIT)])
        res = a.transform([(H_ELES, H_COORDS, H_UNIT)])
        expected = numpy.array([[0.5, 0., 0., 0.]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_transform_before_fit(self):
        a = SineMatrix()
        with self.assertRaises(ValueError):
            a.transform([H])

    def test_fit_transform(self):
        a = SineMatrix(input_type=H_INPUT)
        res = a.fit_transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[0.5, 0.475557, 0.475557, 0.5]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_sort(self):
        a = SineMatrix(input_type=H_INPUT, sort=True)
        res = a.fit_transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[0.5, 0.475557, 0.475557, 0.5]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)

    def test_eigen(self):
        a = SineMatrix(input_type=H_INPUT, eigen=True)
        res = a.fit_transform([(H2_ELES, H2_COORDS, H2_UNIT)])
        expected = numpy.array([[0.975557, 0.024443]])
        try:
            numpy.testing.assert_array_almost_equal(
                res,
                expected)
        except AssertionError as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
