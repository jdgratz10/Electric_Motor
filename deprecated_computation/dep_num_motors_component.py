from openmdao.api import ExplicitComponent, Problem

class NumMotors(ExplicitComponent):

    def initialize(self):
        self.options.declare("algorithm", default = "regression", desc = "Tells the component which caluclation algorithm is being used")
        self.options.declare("motors", default = 4, desc = "Number of motors on aircraft")

    def setup(self):

        if self.options["algorithm"] == "regression":
            self.add_input("motor_wt", val = 106.47367303, units = "kg", desc = "Weight of motor alone")
            self.add_input("gb_wt", val = 10.36947702, units = "kg", desc = "Weight of gearbox alone")

        else:
            self.add_input("combined_wt", val = 27.46825587, units = "kg", desc = "Combined weight of motor and gearbox")

        self.add_output("W_motor_gearbox", units = "kg", desc = "weight of all the motors and gearboxes combined")

        if self.options["algorithm"] == "regression":
            self.declare_partials("W_motor_gearbox", ["motor_wt", "gb_wt"], val = self.options["motors"])

        else:
            self.declare_partials("W_motor_gearbox", "combined_wt", val = self.options["motors"])

    def compute(self, inputs, outputs):
        if self.options["algorithm"] == "regression":
            outputs["W_motor_gearbox"] = self.options["motors"] * (inputs["motor_wt"] + inputs["gb_wt"])

        else:
            outputs["W_motor_gearbox"] = self.options["motors"] * inputs["combined_wt"]

def test_num_motors_component(alg = "regression"):
    prob = Problem()
    prob.model = NumMotors(algorithm = alg)

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)

if __name__ == "__main__":

    prob1 = test_num_motors_component()
    prob1.check_partials(compact_print = True, method = "cs")

    print(prob1["W_motor_gearbox"])

    prob2 = test_num_motors_component("computation")
    prob2.check_partials(compact_print = True, method = "cs")

    print(prob2["W_motor_gearbox"])