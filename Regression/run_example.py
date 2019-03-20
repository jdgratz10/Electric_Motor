from openmdao.api import Problem, ScipyOptimizeDriver
from regression_motor_sizing import Regression
from gearbox_weight_component import GearboxWeight
from num_motors import NumMotors
from w_motor_gb import MotorGearbox

### The options for the group "MotorGearbox" are:
    #1) power - default = 500 kW (this is the desired power out of the motor)
    #2) K_gearbox_metric - default = 32.688 (this is a technology factor in metric units)
    #3) prop_RPM - default = 4000 (this is the RPM of the prop attached to the gearbox)
    #4) motor_rpm - default = 20000 (this is the RPM of the motor)
    #5) num_motors - default = 4 (this is the number of motors and gearboxes to calculate the combined weight of)
    #6) keywords - default is the keyword list from the input file (this list specifies the type of motor, and must be input as a list)

### Example regression_motor_sizing, which calculates the weight of a single motor given the desired output power of that motor ###
prob1 = Problem()
prob1.model = Regression()
    
prob1.setup(force_alloc_complex = True)
prob1.run_model()

power = prob1["power"]
motor_weight = prob1["wt"]

print("\nFor a power of %s kW, the motor will weigh %s kg\n" %(power, motor_weight))


### Example of gearbox_weight_component, which calculates the weight of a single gearbox ###
    
prob2 = Problem()
prob2.model = GearboxWeight()

prob2.setup(force_alloc_complex = True)
prob2.run_model()

power = prob2["HP_out"]
gearbox_weight = prob2["wt"]

print("For a power of %s hp, the gearbox will weigh %s kg\n" %(power, gearbox_weight))

### Example of num_motors, which calculates the total weight of all combined motors and gearboxes ###

prob3 = Problem()
prob3.model = NumMotors()

prob3.setup(force_alloc_complex = True)
prob3.run_model()

motor_wt = prob3["motor_wt"]
gb_wt = prob3["gb_wt"]
W_motor_gearbox = prob3["W_motor_gearbox"]

print("For an individual motor weight of %s kg and an individual gearbox weight of %s kg, the total weight of all motor gearbox assemblies is %s\n" %(motor_wt, gb_wt, W_motor_gearbox))

### Example of w_motor_gb, which is the group that connects the underlying components ###

prob4 = Problem()
prob4.model = MotorGearbox()

prob4.setup(force_alloc_complex = True)
prob4.run_model()

print("The total weight of all motors and gearboxes is %s\n" %(prob4["W_motor_gearbox"]))