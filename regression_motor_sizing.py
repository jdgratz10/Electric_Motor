from collections import namedtuple
from itertools import chain
import numpy as np 
import matplotlib.pyplot as plt 
from openmdao.api import Problem, Group, IndepVarComp, ExplicitComponent

# Motor Specification
# pwr - Rated power (kW)
# pwr_max - Max power, 15 seconds (kW)
# rpm - rated rpm
# rpm_max - max rpm
# gr - gear ratio
# t - torque (N*m)
# t_max - max torque (N*m)
# v - Voltage
# w - Weight (kg)
# eff - efficiency
# cost - cost

# Valid keywords
# -------------------
# 'Aero',       'Auto'
# 'OutRunner',  'InRunner',  'Dual'
# 'Axial',      'Radial'
# 'AirCool',    'LiquidCool'
# 'Direct',     'GearBox' <- not actually valid
# 'Development','Commercial'
# 'BMW','Brusa','Emrax','Joby','Launchpoint','Magicall','MagniX','Magnax','Marand','McLaren','MTS','NeuMotor','Rotex','Safran','Siemens','ThinGap','UQM','YASA' (MTS, Safran, and Marand aren't actually valid)

##################################################################################### User Inputs ######################################################################################################

# the list below is all the relevant keywords
# words = ['Aero', 'Auto', 'OutRunner',  'InRunner',  'Dual', 'Axial',      'Radial', 'AirCool',    'LiquidCool', 'Development','Commercial', 'BMW',
# 'Brusa','Emrax','Joby','Launchpoint','Magicall','MagniX','Magnax','McLaren','NeuMotor','Rotex','Siemens','ThinGap','UQM','YASA']
    
keywords = ["Axial", "Aero", "OutRunner", "LiquidCool"] # user input specifies what keyword to use. Must be a list, even if there is only one keyword
power = 1000. #power = 545.# user input specifies the desired power in units of kW
plot = True # user specifies if they want a plot of their regression
show_motors = True  # user specifies if they want the names of the motors displayed on the regression plot

#################################################################################### Data Collection #######################################################################################################

MotorDatum = namedtuple('MotorDatum',['pwr', 'pwr_max', 'rpm', 'rpm_max', 'gr', 't', 't_max', 'v', 'w', 'eff', 'cost']) 

Motors = (
    ('Brusa HSM1-10.18.04',             MotorDatum(pwr=31, pwr_max=56, rpm=7500, rpm_max=13000, gr=1, t=52, t_max=105, v=400, w=25.0, eff=1, cost=0), set(('Auto','InRunner','Radial','LiquidCool','Commercial','Brusa'))),      
    ('BMW i3 EMP242',                   MotorDatum(pwr=125, pwr_max=125, rpm=4700, rpm_max=5000, gr=3., t=250, t_max=250, v=355, w=41.0, eff=1, cost=0), set(('Auto','InRunner','Radial','LiquidCool','Commercial','BMW'))),      
    ('EMRAX 188-HB-AC',                 MotorDatum(pwr=28, pwr_max=70, rpm=3000, rpm_max=7000, gr=1, t=89, t_max=100, v=400, w=6.8, eff=1, cost=0), set(('Aero','OutRunner','Axial','AirCool','Commercial','Emrax'))),
    ('EMRAX 208-HB-AC',                 MotorDatum(pwr=32, pwr_max=80, rpm=3000, rpm_max=5000, gr=1, t=120, t_max=150, v=470, w=9.1, eff=1, cost=0), set(('Aero','OutRunner','Axial','AirCool','Commercial','Emrax'))),
    ('EMRAX 228-HB-AC',                 MotorDatum(pwr=42, pwr_max=100, rpm=3000, rpm_max=5000, gr=1, t=134, t_max=240, v=670, w=12., eff=1, cost=0), set(('Aero','OutRunner','Axial','AirCool','Commercial','Emrax'))),
    ('EMRAX 268-LV-AC',                 MotorDatum(pwr=75, pwr_max=115, rpm=2000, rpm_max=4000, gr=1, t=250, t_max=500, v=700, w=19.9, eff=1, cost=0), set(('Aero','OutRunner','Axial','AirCool','Commercial','Emrax'))),
    ('EMRAX 348-LV-AC',                 MotorDatum(pwr=170, pwr_max=330, rpm=4000, rpm_max=4000, gr=1, t=406, t_max=1000, v=340, w=39., eff=1, cost=0), set(('Aero','OutRunner','Axial','AirCool','Commercial','Emrax'))),
   #('EMRAX 348-LV-LC',                 MotorDatum(pwr=180, pwr_max=330, rpm=1800, rpm_max=4000, gr=1, t=500, t_max=1000, v=340, w=40., eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
    ('EMRAX 348-LV-CC',                 MotorDatum(pwr=200, pwr_max=330, rpm=1800, rpm_max=4000, gr=1, t=500, t_max=1000, v=340, w=40., eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
   #('EMRAX 188-LV-LC',                 MotorDatum(pwr=30, pwr_max=70, rpm=3000, rpm_max=7000, gr=1, t=50, t_max=100, v=100, w=7., eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
    ('EMRAX 188-LV-CC',                 MotorDatum(pwr=35, pwr_max=70, rpm=3000, rpm_max=7000, gr=1, t=50, t_max=100, v=100, w=7., eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
   #('EMRAX 208-LV-LC',                 MotorDatum(pwr=32, pwr_max=80, rpm=3000, rpm_max=6000, gr=1, t=80, t_max=150, v=125, w=9.3, eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
    ('EMRAX 208-LV-CC',                 MotorDatum(pwr=40, pwr_max=80, rpm=3000, rpm_max=6000, gr=1, t=80, t_max=150, v=125, w=9.3, eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
   #('EMRAX 228-LV-LC',                 MotorDatum(pwr=42, pwr_max=100, rpm=3000, rpm_max=5500, gr=1, t=125, t_max=240, v=130, w=12.3, eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
    ('EMRAX 228-LV-CC',                 MotorDatum(pwr=55, pwr_max=100, rpm=3000, rpm_max=5500, gr=1, t=125, t_max=240, v=130, w=12.3, eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
    ('EMRAX 268-LV-LC',                 MotorDatum(pwr=80, pwr_max=115, rpm=2300, rpm_max=4500, gr=1, t=250, t_max=500, v=130, w=20.3, eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
   #('EMRAX 2x 348',                    MotorDatum(pwr=293, pwr_max=300, rpm=2800, rpm_max=3000, gr=1, t=1000, t_max=1000, v=800, w=80., eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
    ('EMRAX 348',                       MotorDatum(pwr=168, pwr_max=168, rpm=3200, rpm_max=3200, gr=1, t=500, t_max=500, v=340, w=40., eff=1, cost=0), set(('Aero','OutRunner','Axial','LiquidCool','Commercial','Emrax'))),
    ('Joby JM1',                        MotorDatum(pwr=13, pwr_max=20, rpm=6000, rpm_max=9000, gr=1, t=21, t_max=32, v=40, w=2.7, eff=1, cost=6000), set(('Aero','InRunner','Radial','AirCool','Commercial','Joby'))),
    ('Joby JM1S',                       MotorDatum(pwr=8, pwr_max=13, rpm=6000, rpm_max=9000, gr=1, t=13, t_max=20, v=45, w=1.8, eff=1, cost=6000), set(('Aero','InRunner','Radial','AirCool','Commercial','Joby'))),
    ('Joby JM2',                        MotorDatum(pwr=14, pwr_max=21, rpm=2500, rpm_max=3500, gr=1, t=53, t_max=80, v=100, w=4.0, eff=1, cost=6000), set(('Aero','InRunner','Radial','AirCool','Commercial','Joby'))),
    ('Joby JM2S',                       MotorDatum(pwr=11, pwr_max=16, rpm=2500, rpm_max=3500, gr=1, t=40, t_max=60, v=50, w=3.3, eff=1, cost=6000), set(('Aero','InRunner','Radial','AirCool','Commercial','Joby'))),
    ('Joby JMx57',                      MotorDatum(pwr=60, pwr_max=72, rpm=2250, rpm_max=3500, gr=1, t=255, t_max=400, v=400, w=26.3, eff=1, cost=6000), set(('Aero','OutRunner','Radial','AirCool','Development','Joby'))),
    ('Launchpoint 7.5" DHA-075-6-75-1-4T3PY Housed',
                                        MotorDatum(pwr=6, pwr_max=10, rpm=6000, rpm_max=7000, gr=1, t=10, t_max=13, v=270., w=1.5, eff=1, cost=15000), set(('Aero','Dual','Axial','AirCool','Development','Launchpoint'))),
    ('Launchpoint 12" Direct Drive',    MotorDatum(pwr=10, pwr_max=20, rpm=1500, rpm_max=3000, gr=1, t=64, t_max=64, v=270., w=7.0, eff=1, cost=25000), set(('Aero','Dual','Axial','AirCool','Development','Launchpoint'))),
    ('Launchpoint 5kw',                 MotorDatum(pwr=5, pwr_max=5, rpm=8400, rpm_max=8400, gr=1, t=6, t_max=6, v=0, w=0.7, eff=1, cost=0), set(('Aero','Dual','Axial','AirCool','Development','Launchpoint'))),
    ('Launchpoint 16kw',                MotorDatum(pwr=16, pwr_max=16, rpm=12000, rpm_max=12000, gr=1, t=13, t_max=13, v=0, w=1.5, eff=1, cost=0), set(('Aero','Dual','Axial','AirCool','Development','Launchpoint'))),
    ('Launchpoint 82kw',                MotorDatum(pwr=82, pwr_max=82, rpm=6200, rpm_max=6200, gr=1, t=126, t_max=126, v=0, w=12.7, eff=1, cost=0), set(('Aero','Dual','Axial','AirCool','Development','Launchpoint'))),
    ('Magicall MaGiDRIVE 12',           MotorDatum(pwr=10, pwr_max=12, rpm=7000, rpm_max=7000, gr=1, t=25, t_max=25, v=24, w=2.8, eff=1, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','Magicall'))),
    ('Magicall MaGiDRIVE 20',           MotorDatum(pwr=16, pwr_max=20, rpm=6200, rpm_max=6200, gr=1, t=50, t_max=50, v=24, w=4.8, eff=1, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','Magicall'))),
    ('Magicall MaGiDRIVE 40',           MotorDatum(pwr=32, pwr_max=40, rpm=5500, rpm_max=5500, gr=1, t=100, t_max=100, v=24, w=8.9, eff=1, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','Magicall'))),
    ('Magicall MaGiDRIVE 75',           MotorDatum(pwr=60, pwr_max=75, rpm=5000, rpm_max=5000, gr=1, t=225, t_max=225, v=24, w=16.5, eff=1, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','Magicall'))),
    ('Magicall MaGiDRIVE 150',          MotorDatum(pwr=120, pwr_max=150, rpm=4200, rpm_max=4200, gr=1, t=500, t_max=500, v=24, w=29.7, eff=1, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','Magicall'))),
    ('Magicall MaGiDRIVE 300',          MotorDatum(pwr=240, pwr_max=300, rpm=3600, rpm_max=3600, gr=1, t=1000, t_max=1000, v=24, w=49.5, eff=1, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','Magicall'))),
    ('MagniX Magni5',                   MotorDatum(pwr=265, pwr_max=265, rpm=2500, rpm_max=2500, gr=1, t=1012, t_max=1012, v=24, w=53., eff=1, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','MagniX'))),
    ('MagniX Magni250',                 MotorDatum(pwr=280, pwr_max=280, rpm=1900, rpm_max=1900, gr=1, t=1407, t_max=1407, v=540, w=60., eff=93.8, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','MagniX'))),
    ('MagniX Magni500',                 MotorDatum(pwr=560, pwr_max=560, rpm=1900, rpm_max=1900, gr=1, t=2814, t_max=2814, v=540, w=120., eff=93.8, cost=0), set(('Aero','InRunner','Radial','AirCool','Commercial','MagniX'))),
    ('Magnax AXF225',                   MotorDatum(pwr=170, pwr_max=170, rpm=6500, rpm_max=6500, gr=1, t=250, t_max=250, v=0, w=14., eff=1, cost=0), set(('Aero','Axial','LiquidCool','Commercial','Magnax'))),
    ('McLaren Emotor',                  MotorDatum(pwr=110, pwr_max=120, rpm=17000, rpm_max=17000, gr=9., t=105, t_max=130, v=0, w=26.0, eff=1, cost=0), set(('Auto','InRunner','Radial','LiquidCool','Commercial','McLaren'))),      
    ('NeuMotor8038/LV (66v)' ,          MotorDatum(pwr=15, pwr_max=20, rpm=6000, rpm_max=8000, gr=1, t=24, t_max=24, v=66.6, w=2.0, eff=1, cost=329), set(('Aero','OutRunner','Radial','AirCool','Commercial','NeuMotor'))),
    ('NeuMotor8038/HV (270v)',          MotorDatum(pwr=15, pwr_max=20, rpm=6000, rpm_max=8000, gr=1, t=24, t_max=24, v=270., w=2.0, eff=1, cost=329), set(('Aero','OutRunner','Radial','AirCool','Commercial','NeuMotor'))),
    ('Rotex REX30',                     MotorDatum(pwr=15, pwr_max=18, rpm=2700, rpm_max=2700, gr=1, t=53, t_max=53, v=63., w=5.2, eff=1, cost=0), set(('Aero','OutRunner','Radial','AirCool','Commercial','Rotex'))),
    ('Rotex REX90',                     MotorDatum(pwr=50, pwr_max=60, rpm=2200, rpm_max=2200, gr=1, t=217, t_max=217, v=380., w=17., eff=1, cost=0), set(('Aero','OutRunner','Radial','AirCool','Commercial','Rotex'))),
    ('Siemens SP200D',                  MotorDatum(pwr=204, pwr_max=204, rpm=1300, rpm_max=1300, gr=1, t=1450, t_max=1450, v=580., w=49., eff=95., cost=0), set(('Aero','OutRunner','Radial','LiquidCool','Commercial','Siemens'))),
    ('Siemens SP260D',                  MotorDatum(pwr=260, pwr_max=370, rpm=2500, rpm_max=3500, gr=1, t=993, t_max=1009, v=580., w=50.2, eff=95., cost=0), set(('Aero','OutRunner','Radial','LiquidCool','Commercial','Siemens'))),
    ('ThinGap 10" Dev TGD-260Y083B23',  MotorDatum(pwr=13, pwr_max=15, rpm=1400, rpm_max=2000, gr=1, t=72, t_max=89, v=100., w=5.6, eff=1, cost=17869), set(('Aero','OutRunner','Radial','AirCool','Development','ThinGap'))),
    ('ThinGap 10" Prod TGD-260Y083A231',MotorDatum(pwr=13, pwr_max=20, rpm=2500, rpm_max=2500, gr=1, t=50, t_max=76, v=100., w=6.2, eff=1, cost=15860), set(('Aero','OutRunner','Radial','AirCool','Commercial','ThinGap'))),
    ('ThinGap 10" Carbon Fiber',        MotorDatum(pwr=13, pwr_max=40, rpm=2500, rpm_max=2500, gr=1, t=50, t_max=153, v=270., w=6.2, eff=1, cost=15860), set(('Aero','OutRunner','Radial','AirCool','Commercial','ThinGap'))),
    ('ThinGap 15" CF TGD-386Y045A356-H',MotorDatum(pwr=14.6, pwr_max=20, rpm=9000, rpm_max=9000, gr=1, t=15, t_max=23.6, v=42.4, w=2.0, eff=1, cost=27000), set(('Aero','OutRunner','Radial','AirCool','Development','ThinGap'))),
    ('ThinGap Aurora Canard PF1.0',     MotorDatum(pwr=107, pwr_max=114, rpm=7600, rpm_max=7600, gr=1, t=134, t_max=143, v=235, w=11.3, eff=1, cost=0), set(('Aero','OutRunner','Radial','AirCool','Development','ThinGap'))),
    ('ThinGap Aurora Canard PF0.9',     MotorDatum(pwr=96, pwr_max=103, rpm=7600, rpm_max=7600, gr=1, t=121, t_max=129, v=235, w=11.3, eff=1, cost=0), set(('Aero','OutRunner','Radial','AirCool','Development','ThinGap'))),
    ('ThinGap Aurora Wing PF1.0',       MotorDatum(pwr=141, pwr_max=194, rpm=5848, rpm_max=5848, gr=1, t=229, t_max=317, v=233, w=17.9, eff=1, cost=0), set(('Aero','OutRunner','Radial','AirCool','Development','ThinGap'))),
    ('ThinGap Aurora Wing PF0.9',       MotorDatum(pwr=127, pwr_max=175, rpm=5848, rpm_max=5848, gr=1, t=207, t_max=286, v=233, w=17.9, eff=1, cost=0), set(('Aero','OutRunner','Radial','AirCool','Development','ThinGap'))),
    ('UQM HD250',                       MotorDatum(pwr=150, pwr_max=250, rpm=5500, rpm_max=5500, gr=1, t=360, t_max=900, v=450., w=85., eff=1, cost=0), set(('Auto','OutRunner','Radial','LiquidCool','Commercial','UQM'))),
    ('YASA P400',                       MotorDatum(pwr=60, pwr_max=160, rpm=2250, rpm_max=8000, gr=1, t=255, t_max=370, v=0., w=23.6, eff=1, cost=0), set(('Auto','OutRunner','Radial','LiquidCool','Commercial','YASA'))),
)

#################################################################################### Necessary Function(s) #################################################################################################

def filter_data(keywords): # This function extracts the motor weight, motor power, and motor name for each motor in the data set whose keywords include the keyword specified
    keywords = set(keywords)
    x = []
    y = []
    motors = []
    all_words = Motors[0][2]
    val = False
    
    for i in Motors:
        all_words = set(chain(all_words, i[2]))
        motor_words = i[2]
        if keywords.issubset(motor_words):
            x.append(i[1].pwr)  
            y.append(i[1].w)  
            motors.append(i[0])
            val = True
    if val == False:
        raise Exception("One or more of your keywords: %s are incompatible or not allowed" %(keywords))

    return(x, y, motors)


#################################################################################### OpenMDAO model ####################################################################################################

class Regression(ExplicitComponent): # This component calculates a linear regression and its derivatives for the power and weight of the desired motors.

    def initialize(self):
        self.options.declare("keywords", default = ["Axial"], types = list, desc = "keywords to use in component")

    def setup(self):
        data = filter_data(self.options["keywords"])
        self.raw_power = data[0]     # powers of the motors
        raw_weight = data[1]    # actual weights of the motors
          
        self.coefficients = np.polyfit(self.raw_power, raw_weight, 1)    # coefficients of the linear regression line.  [0] is the slope, and [1] is the y-intercept

        self.add_input("power", val = 500, units = "kW", desc = "power of the motor") 
        self.add_output("wt", units = "kg", desc = "outputted weight of motor")   
        self.add_output("regression_weights", shape = np.shape(self.raw_power), units = "kg", desc = "corresponding fitted weights for regression plot, no actual bearing on model, but used for visual aid")

        self.declare_partials("wt", "power", val = self.coefficients[0])

    def compute(self, inputs, outputs):
        outputs["wt"] = np.add(np.multiply(self.coefficients[0], inputs["power"]), self.coefficients[1])
        outputs["regression_weights"] = np.add(np.multiply(self.coefficients[0], self.raw_power), self.coefficients[1])

class RegressionMotorWeight(Group):

    def setup(self):
        ### set up inputs
        indeps = self.add_subsystem("indeps", IndepVarComp(), promotes = ["*"])
        indeps.add_output("power", power, units = "kW", desc = "power of the motor")
        self.add_subsystem("regression", Regression(keywords = keywords), promotes_inputs = ["power"])

############################################################################################### Test Function ##############################################################################################
def test_regression_component():
    prob = Problem()
    prob.model = Regression()

    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)


def test_regression_motor_weight():
    prob = Problem()
    prob.model = RegressionMotorWeight()
    
    prob.setup(check = False, force_alloc_complex = True)

    prob.run_model()

    return(prob)


if __name__ == "__main__":
    
########################################################################################## OpenMDAO instantiation ##########################################################################################

    prob1 = test_regression_motor_weight()
    
    prob1.check_partials(compact_print = True, method = "cs")
    print("For a power of %s kW, the motor will weigh %s kg" %(prob1["power"], prob1["regression.wt"]))

    prob2 = test_regression_component()
    
    prob2.check_partials(compact_print = True, method = "cs")
    print("For a power of %s kW, the motor will weigh %s kg" %(prob2["power"], prob2["wt"]))

################################################################################################### Plots ##################################################################################################
    if plot == True:
        data = filter_data(keywords)
        data_power = data[0]
        data_weight = data[1]
        motor_names = data[2]
        plt.plot(data_power, data_weight, "o")
        plt.plot(power, prob1["regression.wt"], marker = "o", color = "red")
        plt.plot(data_power, prob1["regression.regression_weights"])
        if show_motors == True:
            for i in np.arange(0, len(motor_names), 1):
                plt.annotate("%s" % motor_names[i], xy = (data_power[i], prob1["regression.regression_weights"][i]), textcoords = "data")

        plt.title(f"Motor Keywords: '{keywords}'")
        plt.xlabel("Power (kW)")
        plt.ylabel("Weight (kg)")
        plt.legend(["Actual Motors", "Your Motor", "Regression Line"])
        plt.show()