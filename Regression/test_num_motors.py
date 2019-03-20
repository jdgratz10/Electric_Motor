import unittest
from openmdao.utils.assert_utils import assert_rel_error, assert_check_partials

from num_motors import test_num_motors

class TestNumMotors(unittest.TestCase):

    def test_motors(self):
        prob = test_num_motors()

        assert_rel_error(self, prob["W_motor_gearbox"], 408.95611088, 1e-4)

        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)

if __name__ == "__main__":

    unittest.main()