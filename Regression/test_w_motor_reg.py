import unittest
from openmdao.utils.assert_utils import assert_rel_error, assert_check_partials

from regression_motor_sizing import test_regression_motor_sizing

class TestRegressionMotorSizing(unittest.TestCase):

    def test_motor_sizing(self):
        prob = test_regression_motor_sizing()

        assert_rel_error(self, prob["wt"], 91.8695507, 1e-4)
        
        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)

if __name__ == "__main__":

    unittest.main()