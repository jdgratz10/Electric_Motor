from openmdao.api import Problem, Group, IndepVarComp, ScipyOptimizeDriver
import regression_sizing as reg
import computational_inputs as comp
from gearbox_weight_component import Gearbox_Weight
from computational_sizing_component import Objective_Weight

### Below is a list of the valid keywords for the motor
# ['Aero', 'Auto', 'OutRunner',  'InRunner',  'Dual', 'Axial',      'Radial', 'AirCool',    'LiquidCool', 'Development','Commercial', 'BMW',
# 'Brusa','Emrax','Joby','Launchpoint','Magicall','MagniX','Magnax','McLaren','NeuMotor','Rotex','Siemens','ThinGap','UQM','YASA']

### The two acceptable strings for algorithm type are: "computation" and "regression"
class Weight(Group):

    def initialize(self):
        self.options.declare("algorithm", default = "computation", desc = "Tells the group which algorithm to execute")
        self.options.declare("power", desc = "Power required from motor to size in kW")
        self.options.declare("max_RPM", default = 20000, desc = "Maximum limit on optimizer if running computational algorithm")
        self.options.declare("max_trq", default = 0, desc = "Maximum limit on torque for optimizer if running computational algorithm")
        self.options.declare("min_RPM", default = 1000, desc = "Minimum limit on optimizer if running computational algorithm")
        self.options.declare("min_trq", default = 0, desc = "Minimum limit on torque for optimizer if running computational algorithm")
        self.options.declare("keywords", default = comp.keywords, types = list, desc = "Keywords to use in regression calculation")

    def setup(self):
        ### perform basic calculations and variable initializations
        horsepower = self.options["power"] * 1.34102  
        if self.options["algorithm"] == "regression":
            ### set up inputs
            indeps = self.add_subsystem("indeps", IndepVarComp())
            indeps.add_output("power", self.options["power"], units = "kW", desc = "Output power of the motor")
            indeps.add_output("HP_out", horsepower, units = "hp", desc = "Outpt power of the motor in HP")
            indeps.add_output("K_gearbox_metric", comp.K_gearbox_metric, desc = "Technology level of gearbox")
            indeps.add_output("prop_RPM", comp.prop_RPM, units = "rpm", desc = "Propeller RPM, slower gearbox speed")
            indeps. add_output("motor_speed", self.options["max_RPM"], units = "rpm", desc = "Motor speed")
            ### create connections
            self.add_subsystem("regression", reg.Regression(keywords = self.options["keywords"]))
            self.add_subsystem("gearbox", Gearbox_Weight())
            self.connect("indeps.power", "regression.power")
            self.connect("indeps.HP_out", "gearbox.HP_out")
            self.connect("indeps.K_gearbox_metric", "gearbox.K_gearbox_metric")
            self.connect("indeps.prop_RPM", "gearbox.R_RPM")
            self.connect("indeps.motor_speed", "gearbox.motor_speed")

        elif self.options["algorithm"] == "computation": 

            if prob.model.options["max_trq"] != 0:
                prob.model.options["max_RPM"] = horsepower * 5252 / prob.model.options["max_trq"]      
        
            if prob.model.options["min_trq"] != 0:
                prob.model.options["min_RPM"] = horsepower * 5252 / prob.model.options["min_trq"]

            if prob.model.options["min_RPM"] > prob.model.options["max_RPM"]:
                raise Exception("The minimum RPM is greater than the maximum RPM")
            
            ### set up inputs
            indeps = self.add_subsystem("indeps", IndepVarComp())
            indeps.add_output("Motor_Density", comp.Motor_Density, units = "kg / m**3", desc = "Volumetric Density of entire motor")
            indeps.add_output("P_out", self.options["power"], units = "kW", desc = "Output power of motor in W")
            indeps.add_output("HP_out", horsepower, units = "hp", desc = "Output power of motor in HP")
            indeps.add_output("S_stress", comp.S_stress, units = "Pa", desc = "Magnetic shear stress of motor")
            indeps.add_output("P_factor", comp.P_factor, desc = "Power factor of motor")
            indeps.add_output("K_gearbox_metric", comp.K_gearbox_metric, desc = "Technology level of gearbox")
            indeps.add_output("prop_RPM", comp.prop_RPM, units = "rpm", desc = "Prop RPM, slower gearbox speed")
            indeps.add_output("motor_speed", self.options["max_RPM"], units = "rpm", desc = "Motor speed, the value that will be varied by the optimizer")
            ### create connections
            self.add_subsystem("computation", Objective_Weight())
            self.connect("indeps.Motor_Density", "computation.Motor_Density")
            self.connect("indeps.P_out", "computation.P_out")
            self.connect("indeps.HP_out", "computation.HP_out")
            self.connect("indeps.S_stress", "computation.S_stress")
            self.connect("indeps.P_factor", "computation.P_factor")
            self.connect("indeps.K_gearbox_metric", "computation.K_gearbox_metric")
            self.connect("indeps.prop_RPM", "computation.R_RPM")
            self.connect("indeps.motor_speed", "computation.motor_speed")
        else:
            raise Exception("You have specified an algorithm of %s, which does not exist" %(self.options["algorithm"]))


prob = Problem()
prob.model = Weight(algorithm = "regression", power = 500)
prob.setup()

if prob.model.options["algorithm"] == "regression":
    
    prob.run_model()
    
    power = prob["indeps.power"]
    total_weight = prob["regression.wt"] + prob["gearbox.wt"]
    motor_RPM = prob["indeps.motor_speed"]

elif prob.model.options["algorithm"] == "computation":
    
    prob.model.add_design_var("indeps.motor_speed", lower = prob.model.options["min_RPM"], upper = prob.model.options["max_RPM"])
    prob.model.add_objective("computation.wt")
    
    prob.driver = ScipyOptimizeDriver()
    prob.driver.options["maxiter"] = 20000
    prob.driver.options["optimizer"] = "COBYLA"

    prob.setup()
    prob.run_driver()
    # prob.run_model()

    power = prob["indeps.P_out"]
    total_weight = prob["computation.wt"]
    motor_RPM = prob["indeps.motor_speed"]

print("\nThe algorithm type is: %s" %prob.model.options["algorithm"])
print("For a power of %s kW at an RPM of %s, the motor and gearbox will weigh %s kg" %(power, motor_RPM, total_weight))