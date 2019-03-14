from openmdao.api import Problem, ScipyOptimizeDriver
from switch_sizing_method import Weight

### The options for the group "Weight" are:
    #1) algorithm - default = "regression" (this tells the group which algorithms to use.  The options are "regression" and "computation" (unreliable))
    #2) power - default = 500 kW (this is the desired power out of the motor)
    #3) max_RPM - default = 20,000 RPM (this sets the speed of the motor for the gearbox weight calculation in regression mode, and the upper limit to motor speed in computation mode)
    #4) min_RPM - default = 1,000 RPM (this sets the lower limit to motor speed in computation mode, and is ignored in regression mode)
    #5) max_trq - default = 0 because this value isn't used unless it is set (if specified, this value is used to calculate a max motor RPM in computation mode, and is ignored in regression mode)
    #6) min_trq - default = 0 because this value isn't used unless it is set (if specified, this value is used to calculate a min motor RPM in computation mode, and is ignored in regression mode)
    #7) keywords - default is the keyword list from the input file (this list specified the types of motors to be used in regression mode, and is ignored in computation mode)

### Example with regression algorithm ###
prob1 = Problem()
prob1.model = Weight()
    
prob1.setup(force_alloc_complex = True)
prob1.run_model()

power = prob1["indeps.power"]
total_weight = prob1["regression.wt"] + prob1["gearbox.wt"]
motor_RPM = prob1["indeps.motor_speed"]

print("\nThe algorithm type is: %s" %prob1.model.options["algorithm"])
print("For a power of %s kW at an RPM of %s, the motor and gearbox will weigh %s kg\n" %(power, motor_RPM, total_weight))


### Example with computation algorithm (this algorithm not recommended, results are questionable) ###
print("Caution: The computational method used for motor weight estimation is inaccurate")
    
prob2 = Problem()
prob2.model = Weight(algorithm = "computation")

prob2.model.add_design_var("indeps.motor_speed", lower = prob2.model.options["min_RPM"], upper = prob2.model.options["max_RPM"])
prob2.model.add_objective("computation.wt")
    
prob2.driver = ScipyOptimizeDriver()
prob2.driver.options["maxiter"] = 20000
prob2.driver.options["optimizer"] = "COBYLA"

prob2.setup(force_alloc_complex = True)
prob2.run_driver()

power = prob2["indeps.P_out"]
total_weight = prob2["computation.wt"]
motor_RPM = prob2["indeps.motor_speed"]

print("\nThe algorithm type is: %s" %prob2.model.options["algorithm"])
print("For a power of %s kW at an RPM of %s, the motor and gearbox will weigh %s kg\n" %(power, motor_RPM, total_weight))