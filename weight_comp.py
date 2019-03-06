from openmdao.api import ExplicitComponent
from math import pi

class Objective_Weight(ExplicitComponent):

    def setup(self):
        self.add_input("Motor_Density", units = "kg / m**3", desc = "Volumetric Density of entire motor")
        self.add_input("P_out", units = "W", desc = "Output power of motor in W")
        self.add_input("HP_out", units = "hp", desc = "Output power of motor in HP")
        self.add_input("S_stress", units = "Pa", desc = "Magnetic shear stress of motor in Pascals")
        self.add_input("P_factor", desc = "Power factor of motor")
        self.add_input("K_gearbox_metric", desc = "Technology level of gearbox")
        self.add_input("R_RPM", units = "rpm", desc = "Rotor RPM, slower gearbox speed in RPM")
        self.add_input("var_speed", units = "rpm", desc = "Motor speed, the value that will be varied by the optimizer in RPM")

        self.add_output("wt", desc = "weight of motor and gearbox")

        self.declare_partials("wt", "var_speed")
        self.declare_partials("wt", "Motor_Density")
        self.declare_partials("wt", "P_out")
        self.declare_partials("wt", "HP_out")
        self.declare_partials("wt", "S_stress")
        self.declare_partials("wt", "P_factor")
        self.declare_partials("wt", "K_gearbox_metric")
        self.declare_partials("wt", "R_RPM")

    def compute(self, inputs, outputs):
        rho = inputs["Motor_Density"]
        P_out = inputs["P_out"]
        HP_out = inputs["HP_out"]
        S_stress = inputs["S_stress"]
        P_factor = inputs["P_factor"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        var_speed = inputs["var_speed"]

        outputs["wt"] = rho * (pi / 4) * 60 * P_out / (pi**2 * S_stress * P_factor * var_speed) + K_gearbox * HP_out**.76 * var_speed**.13 / R_RPM**.89 
        # motor = rho * (pi / 4) * 60 * P_out / (pi**2 * S_stress * P_factor * var_speed * .95)
        # print("Motor Weight: ", motor)

    def compute_partials(self, inputs, J):
        rho = inputs["Motor_Density"]
        P_out = inputs["P_out"]
        HP_out = inputs["HP_out"]
        S_stress = inputs["S_stress"]
        P_factor = inputs["P_factor"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        var_speed = inputs["var_speed"]
        
        J["wt", "var_speed"] = -rho * (pi / 4) * 60 * P_out / (pi**2 * S_stress * P_factor * var_speed**2) + K_gearbox * HP_out**.76 * .13 / (R_RPM**.89 * var_speed**.87)
        J["wt", "Motor_Density"] = pi / 4 * 60 * P_out / (pi**2 * S_stress * P_factor * var_speed)
        J["wt", "P_out"] = rho * (pi / 4) * 60 / (pi**2 * S_stress * P_factor * var_speed)
        J["wt", "HP_out"] = .76 * K_gearbox * HP_out**(-.24) * var_speed**.13 / (R_RPM**.89)
        J["wt", "S_stress"] = -rho * (pi / 4) * 60 * P_out / (pi**2 * S_stress**2 * P_factor * var_speed)
        J["wt", "P_factor"] = -rho * (pi / 4) * 60 * P_out / (pi**2 * S_stress * P_factor**2 * var_speed)
        J["wt", "K_gearbox_metric"] = HP_out**.76 * var_speed**.13 / (R_RPM**.89)
        J["wt", "R_RPM"] = -.89 * K_gearbox * HP_out**.76 * var_speed**.13 / (R_RPM**1.89)