from openmdao.api import ExplicitComponent, Problem

class GearboxWeight(ExplicitComponent):
    
    def setup(self):
        self.add_input("HP_out", val = 670.511044, units = "hp", desc = "Output power of motor")
        self.add_input("K_gearbox_metric", val = 32.688, desc = "Technology level of gearbox")    
        self.add_input("R_RPM", val = 4000, units = "rpm", desc = "Rotor RPM, slower gearbox speed")
        self.add_input("motor_speed", val = 20000, units = "rpm", desc = "Motor speed")
        
        self.add_output("wt", desc = "weight of the gearbox")

        self.declare_partials("wt", ["R_RPM", "K_gearbox_metric", "motor_speed","HP_out"])

    def compute(self, inputs, outputs):
        HP_out = inputs["HP_out"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        motor_speed = inputs["motor_speed"]

        outputs["wt"] = K_gearbox * HP_out**.76 * motor_speed**.13 / R_RPM**.89 
        # Output equation based off of NPSS Electric Machine and Gearbox Sizing Tool for Electric Aircraft Applications by Nathaniel Renner, James L. Felder, and Peter E. Kascak

    def compute_partials(self, inputs, J):
        HP_out = inputs["HP_out"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        motor_speed = inputs["motor_speed"]

        J["wt", "motor_speed"] = K_gearbox * HP_out**.76 * .13 / (R_RPM**.89 * motor_speed**.87)
        J["wt", "HP_out"] = .76 * K_gearbox * HP_out**(-.24) * motor_speed**.13 / (R_RPM**.89)
        J["wt", "K_gearbox_metric"] = HP_out**.76 * motor_speed**.13 / (R_RPM**.89)
        J["wt", "R_RPM"] = -.89 * K_gearbox * HP_out**.76 * motor_speed**.13 / (R_RPM**1.89)

def test_gearbox_weight():
    prob = Problem()
    prob.model = GearboxWeight()

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)

if __name__ == "__main__":

    prob = test_gearbox_weight()
    prob.check_partials(compact_print = True, method = "cs")

    print(prob["wt"])

