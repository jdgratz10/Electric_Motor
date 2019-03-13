from openmdao.api import ExplicitComponent

class Gearbox_Weight(ExplicitComponent):
    
    def setup(self):
        self.add_input("HP_out", units = "hp", desc = "Output power of motor")
        self.add_input("K_gearbox_metric", desc = "Technology level of gearbox")
        self.add_input("R_RPM", units = "rpm", desc = "Rotor RPM, slower gearbox speed")
        self.add_input("motor_speed", units = "rpm", desc = "Motor speed")
        
        self.add_output("wt", desc = "weight of the gearbox")

        self.declare_partials("wt", "motor_speed")
        self.declare_partials("wt", "HP_out")
        self.declare_partials("wt", "K_gearbox_metric")
        self.declare_partials("wt", "R_RPM")

    def compute(self, inputs, outputs):
        HP_out = inputs["HP_out"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        motor_speed = inputs["motor_speed"]

        outputs["wt"] = K_gearbox * HP_out**.76 * motor_speed**.13 / R_RPM**.89 

    def compute_partials(self, inputs, J):
        HP_out = inputs["HP_out"]
        K_gearbox = inputs["K_gearbox_metric"]
        R_RPM = inputs["R_RPM"]
        motor_speed = inputs["motor_speed"]

        J["wt", "motor_speed"] = K_gearbox * HP_out**.76 * .13 / (R_RPM**.89 * motor_speed**.87)
        J["wt", "HP_out"] = .76 * K_gearbox * HP_out**(-.24) * motor_speed**.13 / (R_RPM**.89)
        J["wt", "K_gearbox_metric"] = HP_out**.76 * motor_speed**.13 / (R_RPM**.89)
        J["wt", "R_RPM"] = -.89 * K_gearbox * HP_out**.76 * motor_speed**.13 / (R_RPM**1.89)