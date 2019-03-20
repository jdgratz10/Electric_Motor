from openmdao.api import ExplicitComponent, Problem

class NumMotors(ExplicitComponent):

    def initialize(self):
        self.options.declare("num_motors", default = 4, desc = "Number of motors whose weight to calculate")

    def setup(self):
        self.add_input("motor_wt", val = 91.8695507, units = "kg", desc = "Weight of one motor")
        self.add_input("gb_wt", val = 10.36947702, units = "kg", desc = "Weight of one gearbox")
        self.add_output("W_motor_gearbox", units = "kg", desc = "Weight of all the motors and gearboxes combined")

        self.declare_partials("W_motor_gearbox", ["motor_wt", "gb_wt"], val = self.options["num_motors"])

    def compute(self, inputs, outputs):
        motor_wt = inputs["motor_wt"]
        gb_wt = inputs["gb_wt"]
        num_motors = self.options["num_motors"]

        outputs["W_motor_gearbox"] = num_motors * (motor_wt + gb_wt)

def test_num_motors():
    prob = Problem()
    prob.model = NumMotors()

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)

if __name__ == "__main__":

    prob = test_num_motors()
    prob.check_partials(compact_print = True, method = "cs")

    print(prob["W_motor_gearbox"])

