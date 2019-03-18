import unittest
from openmdao.utils.assert_utils import assert_rel_error, assert_check_partials

from num_motors_component import test_num_motors_component

class TestNumMotors(unittest.TestCase):

    def test_regression(self):
        prob = test_num_motors_component()

        assert_rel_error(self, prob["W_motor_gearbox"], 467.3726002, 1e-4)

        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)

    def test_computation(self):
        prob = test_num_motors_component("computation")

        assert_rel_error(self, prob["W_motor_gearbox"], 109.87302348, 1e-4)

        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)

if __name__ == "__main__":
    unittest.main()