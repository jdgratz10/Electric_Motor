from openmdao.api import Problem, Group
import motor_specification_clean as reg
import motor_gearbox_sizing_openmdao as comp

switch_algorithm = "Regression"
switch_algorithm = "Calculate"
# power = 1   # units = hp

prob = Problem()
prob.model = reg.Regression_Weight()
prob.setup()
prob.run_model()
print("For a power of %s kW, the motor will weigh %s kg" %(prob["indeps.power"], prob["regression.wt"]))

prob = Problem()
prob.model = comp.Computational_Weight()
prob.setup()
prob.run_model()

print("For a power of %s kW, the motor will weigh %s kg" %(prob["indeps.power"], prob["regression.wt"]))

