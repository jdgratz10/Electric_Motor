import unittest
from openmdao.utils.assert_utils import assert_rel_error, assert_check_partials

from w_motor_gb import test_w_motor_gb

class TestWMotorGearbox(unittest.TestCase):

    def test_weight(self):
        prob = test_w_motor_gb()

        assert_rel_error(self, prob["W_motor_gearbox"], 408.95615459, 1e-4)

        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)

if __name__ == "__main__":

    unittest.main()