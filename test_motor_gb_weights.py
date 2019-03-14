import unittest
from openmdao.utils.assert_utils import assert_rel_error, assert_check_partials

from switch_sizing_method import test_motor_weight_reg, test_motor_weight_comp

class TestMotorWeight(unittest.TestCase):

    def test_reg(self):
        prob = test_motor_weight_reg()

        assert_rel_error(self, prob["regression.wt"], 106.47367303, 1e-4)
        assert_rel_error(self, prob["gearbox.wt"], 10.36947702, 1e-4)

        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)


    def test_comp(self):
        prob = test_motor_weight_comp()

        assert_rel_error(self, prob["computation.wt"], 27.46825587, 1e-4)

        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)

if __name__ == "__main__":

    unittest.main()
