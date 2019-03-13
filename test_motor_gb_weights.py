import unittest

from openmdao.api import Problem, IndepVarComp
from openmdao.utils.assert_utils import assert_rel_error, assert_check_partials

from weight_comp import Objective_Weight  

class TestMotorWeight(unittest.TestCase):
    
    def test1(self):
        p = Problem()
        p.model = Objective_Weight()
        p.setup()
        p['P_out'] = 400.
        p.run_model()
        
        assert_rel_error(self, p['wt'], 1910.8593171, 1e-4)
        
        cpd = p.check_partials(compact_print=True, show_only_incorrect=True, method='cs') 
        assert_check_partials(cpd, atol=2e-3, rtol=2e-3)
        


if __name__ == "__main__":

    unittest.main()