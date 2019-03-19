import unittest
from openmdao.utils.assert_utils import assert_rel_error, assert_check_partials

from computational_sizing_component import test_motor_gearbox_weight

class TestMotorGearboxWeight(unittest.TestCase):

    def test1(self):
        prob = test_motor_gearbox_weight()

        assert_rel_error(self, prob["wt"], 50.24144868, 1e-4)

        cpd = prob.check_partials(compact_print = True, show_only_incorrect = True, method = "cs")
        assert_check_partials(cpd, atol = 1e-6, rtol = 1e-6)

if __name__ == "__main__":

    unittest.main()