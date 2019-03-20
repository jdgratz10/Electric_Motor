from openmdao.api import Problem, Group, IndepVarComp
from regression_motor_sizing import Regression
from gearbox_weight_component import GearboxWeight
from num_motors import NumMotors 

class MotorGearbox(Group):

    def initialize(self):
        self.options.declare("power", default = 500, desc = "Power required from each motor")
        self.options.declare("K_gearbox_metric", default = 32.688, desc = "Technology level of gearbox")
        self.options.declare("prop_RPM", default = 4000, desc = "Propeller RPM, slower gearbox speed in RPM")
        self.options.declare("motor_rpm", default = 20000, desc = "Motor speed in RPM")
        self.options.declare("num_motors", default = 4, desc = "Number of motors")
        self.options.declare("keywords", default = ["Axial"], types = list, desc = "Keywords to specify type of motor")

    def setup(self):
        ### set up inputs
        indeps = self.add_subsystem("indeps", IndepVarComp(), promotes = ["*"])
        indeps.add_output("power", self.options["power"], units = "kW", desc = "Output power of each motor")
        indeps.add_output("K_gearbox_metric", self.options["K_gearbox_metric"], desc = "Empirical factor determined by technology level")
        indeps.add_output("prop_RPM", self.options["prop_RPM"], units = "rpm", desc = "Rotational speed of prop attached to gearbox")
        indeps.add_output("motor_rpm", self.options["motor_rpm"], units = "rpm", desc = "Rotational speed of motor")
        ### create connections
        self.add_subsystem("motor", Regression(keywords = self.options["keywords"]), promotes_inputs = ["power"])
        self.add_subsystem("gearbox", GearboxWeight(), promotes_inputs = ["K_gearbox_metric"])
        self.add_subsystem("combine", NumMotors(num_motors = self.options["num_motors"]), promotes_outputs = ["W_motor_gearbox"])
        self.connect("power", "gearbox.HP_out")
        self.connect("prop_RPM", "gearbox.R_RPM")
        self.connect("motor_rpm", "gearbox.motor_speed")
        self.connect("motor.wt", "combine.motor_wt")
        self.connect("gearbox.wt", "combine.gb_wt")


def test_w_motor_gb():
    prob = Problem()
    prob.model = MotorGearbox()

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)

if __name__ == "__main__":
    
    prob = test_w_motor_gb()
    prob.check_partials(compact_print = True, method = "cs")

    print(prob["W_motor_gearbox"])