from openmdao.api import Problem, Group, IndepVarComp, ScipyOptimizeDriver
from warnings import warn as wrn
from regression_motor_sizing import Regression
import input_file as input_file
from gearbox_weight_component import GearboxWeight
from computational_sizing_component import MotorGearboxWeight
from num_motors_component import NumMotors

### Below is a list of the valid keywords for the motor
# ['Aero', 'Auto', 'OutRunner',  'InRunner',  'Dual', 'Axial',      'Radial', 'AirCool',    'LiquidCool', 'Development','Commercial', 'BMW',
# 'Brusa','Emrax','Joby','Launchpoint','Magicall','MagniX','Magnax','McLaren','NeuMotor','Rotex','Siemens','ThinGap','UQM','YASA']

### The two acceptable strings for algorithm type are: "computation" and "regression"


### Top level group to switch between algorithms ###
class MotorGearbox(Group):

    def initialize(self):
        self.options.declare("algorithm", default = "regression", desc = "Tells the group which algorithm to execute")
        self.options.declare("power", default = 500, desc = "Power required from motor to size in kW")
        self.options.declare("max_RPM", default = 20000, desc = "Maximum limit on optimizer if running computational algorithm")
        self.options.declare("min_RPM", default = 1000, desc = "Minimum limit on optimizer if running computational algorithm")
        self.options.declare("max_trq", default = 0, desc = "Maximum limit on torque for optimizer if running computational algorithm")
        self.options.declare("min_trq", default = 0, desc = "Minimum limit on torque for optimizer if running computational algorithm")
        self.options.declare("keywords", default = input_file.keywords, types = list, desc = "Keywords to use in regression calculation")

    def setup(self):
        ### perform basic calculations and variable initializations
        horsepower = self.options["power"] * 1.34102  
        if self.options["algorithm"] == "regression":
            ### set up inputs
            indeps = self.add_subsystem("indeps", IndepVarComp(), promotes = ["*"])
            indeps.add_output("power", self.options["power"], units = "kW", desc = "Output power of the motor")
            indeps.add_output("HP_out", horsepower, units = "hp", desc = "Outpt power of the motor in HP")
            indeps.add_output("K_gearbox_metric", input_file.K_gearbox_metric, desc = "Technology level of gearbox")
            indeps.add_output("prop_RPM", input_file.prop_RPM, units = "rpm", desc = "Propeller RPM, slower gearbox speed")
            indeps. add_output("motor_speed", self.options["max_RPM"], units = "rpm", desc = "Motor speed")
            ### create connections
            self.add_subsystem("motor", Regression(keywords = self.options["keywords"]), promotes_inputs = ["power"])
            self.add_subsystem("gearbox", GearboxWeight(), promotes_inputs = ["HP_out", "K_gearbox_metric", "motor_speed"])
            self.add_subsystem("multiply", NumMotors(motors = 4), promotes_outputs = ["W_motor_gearbox"])
            self.connect("prop_RPM", "gearbox.R_RPM")
            self.connect("motor.wt", "multiply.motor_wt")
            self.connect("gearbox.wt", "multiply.gb_wt")

        elif self.options["algorithm"] == "computation": 
            wrn("The computational method used for motor weight estimation is still a work in progress and currently inaccurate", Warning)

            ### calculate torque from RPM if torque is provided
            if self.options["max_trq"] != 0:
                if self.options["max_RPM"] != 20000:
                    wrn("Warning: Cannot specify both max torque and max RPM. Max RPM value ignored", Warning)
            
                self.options["max_RPM"] = horsepower * 5252 / self.options["max_trq"]      
        
            if self.options["min_trq"] != 0:
                if self.options["min_RPM"] != 1000:
                    wrn("Warning: Cannot specify both min torque and min RPM. Max RPM value ignored", Warning)

                self.options["min_RPM"] = horsepower * 5252 / self.options["min_trq"]

            if self.options["min_RPM"] > self.options["max_RPM"]:
                raise Exception("The minimum RPM is greater than the maximum RPM")
            
            ### set up inputs
            indeps = self.add_subsystem("indeps", IndepVarComp(), promotes = ["*"])
            indeps.add_output("Motor_Density", input_file.Motor_Density, units = "kg / m**3", desc = "Volumetric Density of entire motor")
            indeps.add_output("power", self.options["power"], units = "kW", desc = "Output power of motor in W")
            indeps.add_output("HP_out", horsepower, units = "hp", desc = "Output power of motor in HP")
            indeps.add_output("S_stress", input_file.S_stress, units = "Pa", desc = "Magnetic shear stress of motor")
            indeps.add_output("P_factor", input_file.P_factor, desc = "Power factor of motor")
            indeps.add_output("K_gearbox_metric", input_file.K_gearbox_metric, desc = "Technology level of gearbox")
            indeps.add_output("prop_RPM", input_file.prop_RPM, units = "rpm", desc = "Prop RPM, slower gearbox speed")
            indeps.add_output("motor_speed", self.options["max_RPM"], units = "rpm", desc = "Motor speed, the value that will be varied by the optimizer")
            
            ### create connections
            self.add_subsystem("combined_motor_gb", MotorGearboxWeight(), promotes_inputs=["HP_out", "Motor_Density", "S_stress", "P_factor", "K_gearbox_metric", "motor_speed"])
            self.add_subsystem("multiply", NumMotors(motors = 4, algorithm = "computation"), promotes_outputs = ["W_motor_gearbox"])
            self.connect("power", "combined_motor_gb.P_out")
            self.connect("prop_RPM", "combined_motor_gb.R_RPM")
            self.connect("combined_motor_gb.wt", "multiply.combined_wt")
        else:
            raise Exception("You have specified an algorithm of %s, which does not exist" %(self.options["algorithm"]))


### Test Functions ### 
def test_motor_weight_reg():
    prob = Problem()
    prob.model = MotorGearbox()

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)

def test_motor_weight_comp():
    prob = Problem()
    prob.model = MotorGearbox(algorithm = "computation")
    wrn("The computational method used for motor weight estimation is still a work in progress and currently inaccurate", Warning)
    
    prob.model.add_design_var("motor_speed", lower = prob.model.options["min_RPM"], upper = prob.model.options["max_RPM"])
    prob.model.add_objective("combined_motor_gb.wt")
    
    prob.driver = ScipyOptimizeDriver()
    prob.driver.options["maxiter"] = 20000
    prob.driver.options["optimizer"] = "COBYLA"

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_driver()
    # prob.run_model()

    return(prob)


if __name__ == "__main__":

    prob1 = test_motor_weight_reg()

    prob1.check_partials(compact_print = True, method = "cs")
    print("\nThe algorithm type is: %s" %prob1.model.options["algorithm"])
    print("For a power of %s kW at an RPM of %s, the motor and gearbox will weigh %s kg\n" %(prob1["indeps.power"], prob1["indeps.motor_speed"], prob1["W_motor_gearbox"]))

    prob2 = test_motor_weight_comp()

    prob2.check_partials(compact_print = True, method = "cs")
    print("\nThe algorithm type is: %s" %prob2.model.options["algorithm"])
    print("For a power of %s kW at an RPM of %s, the motor and gearbox will weigh %s kg\n" %(prob2["power"], prob2["motor_speed"], prob2["W_motor_gearbox"]))