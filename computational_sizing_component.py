from openmdao.api import ExplicitComponent, Problem
from math import pi

class MotorGearboxWeight(ExplicitComponent):

    def setup(self):
        self.add_input("Motor_Density", val = 3279.626, units = "kg / m**3", desc = "Volumetric Density of entire motor")
        self.add_input("P_out", val = 1000, units = "kW", desc = "Output power of motor")
        self.add_input("HP_out", val = 1341.02, units = "hp", desc = "Output power of motor in HP")
        self.add_input("S_stress", val = 24.1 * 10**3, units = "Pa", desc = "Magnetic shear stress of motor")
        self.add_input("P_factor", val = .95, desc = "Power factor of motor")
        self.add_input("K_gearbox_metric", val = 32.688, desc = "Technology level of gearbox")
        self.add_input("R_RPM", val = 4000, units = "rpm", desc = "Rotor RPM, slower gearbox speed")
        self.add_input("motor_speed", val = 21000, units = "rpm", desc = "Motor speed, the value that will be varied by the optimizer")

        self.add_output("wt", desc = "weight of motor and gearbox")

        self.declare_partials("wt", ["motor_speed", "Motor_Density", "P_out", "HP_out", "S_stress", "P_factor", "K_gearbox_metric", "R_RPM"])

    def compute(self, inputs, outputs):
        rho = inputs["Motor_Density"]
        P_out = inputs["P_out"]
        HP_out = inputs["HP_out"]
        S_stress = inputs["S_stress"]
        P_factor = inputs["P_factor"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        motor_speed = inputs["motor_speed"]

        outputs["wt"] = rho * (pi / 4) * 60 * P_out * 1000 / (pi**2 * S_stress * P_factor * motor_speed) + K_gearbox * HP_out**.76 * motor_speed**.13 / R_RPM**.89 

    def compute_partials(self, inputs, J):
        rho = inputs["Motor_Density"]
        P_out = inputs["P_out"]
        HP_out = inputs["HP_out"]
        S_stress = inputs["S_stress"]
        P_factor = inputs["P_factor"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        motor_speed = inputs["motor_speed"]
        
        J["wt", "motor_speed"] = -rho * (pi / 4) * 60 * P_out * 1000 / (pi**2 * S_stress * P_factor * motor_speed**2) + K_gearbox * HP_out**.76 * .13 / (R_RPM**.89 * motor_speed**.87)
        J["wt", "Motor_Density"] = pi / 4 * 60 * P_out * 1000 / (pi**2 * S_stress * P_factor * motor_speed)
        J["wt", "P_out"] = rho * 1000 * (pi / 4) * 60 / (pi**2 * S_stress * P_factor * motor_speed)
        J["wt", "HP_out"] = .76 * K_gearbox * HP_out**(-.24) * motor_speed**.13 / (R_RPM**.89)
        J["wt", "S_stress"] = -rho * (pi / 4) * 60 * P_out * 1000 / (pi**2 * S_stress**2 * P_factor * motor_speed)
        J["wt", "P_factor"] = -rho * (pi / 4) * 60 * P_out * 1000 / (pi**2 * S_stress * P_factor**2 * motor_speed)
        J["wt", "K_gearbox_metric"] = HP_out**.76 * motor_speed**.13 / (R_RPM**.89)
        J["wt", "R_RPM"] = -.89 * K_gearbox * HP_out**.76 * motor_speed**.13 / (R_RPM**1.89)

def test_motor_gearbox_weight():
    prob = Problem()
    prob.model = MotorGearboxWeight()

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)

if __name__ == "__main__":

    prob = test_motor_gearbox_weight()
    
    prob.check_partials(compact_print = True, method = "cs")
    print(prob["wt"])
