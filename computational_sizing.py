# Motor + Gearbox Sizing Algorithm
# Originally formulated by Nate Renner, Jim Felder(LTA), Pete Kascak(LED), and Gerry Brown(LMR)
# Ported and extended by Jeff Chin

# The purpose of this tool is to test a motor + gearbox sizing algorithm.
# Using this tool will allow engine and motor experts to collaborate more 
# easily so that designing and integrating advanced electric motors into
# turbo fan engines can become a reality.

# There are three main components to this tool: optimization, 
# motor size mapping, and gearbox size mapping. The optimization uses OpenMDAO
# to optimize the combined weight of the motor and gearbox based on two 
# different equations, one which gives motor volume and one which gives gearbox 
# weight. The motor size mapping involves finding viable design volumes and 
# weights over a range of operating speeds and powers. The current gearbox 
# sizing method uses an existing sizing algorithm based on exisiting gearboxes. 
# Currently, this only provides the weight of the gearbox. 
# Finally, gradient decent optimization is used to minimize the
# combined weight of the motor and the gearbox.

# It is important to note that this tool requires the user to select and
# specific motor topolgy and design. This will likely be based on state of
# the art motors that are currently being developed for this specific
# appliation. 

# To use this tool the following parameters must be known or estimated:
# 1) Magnetic Shear Stress [N/m**2] (This can be derived from magentic and 
#    electric loadings) - S_stress
# 2) Operational Speed of motor [RPM] - n
# 3) Desired Output power of motor [kW] - P_out
# 4) Outer Diameter of Motor [m] - D_out 
# 5) Airgap Diameter of motor [m] - D_ag 
# 6) Number of Poles in motor- pole_num
# 7) Inner and Outer Diameters of All Motor Regions [m] (i.e. air gap, 
#    copper, etc.)
# 8) Density of Material Used in Each Motor Region [kg/m**3]
# 9) Power factor of motor - P_factor 
# 10) Operational Speed of rotor [RPM] - Fan_RPM 
# 11) Technology factor of gearbox - K_gearbox 

from math import pi
import numpy as np
import matplotlib.pyplot as plt
from openmdao.api import Problem, Group, IndepVarComp, ScipyOptimizeDriver
from computational_sizing_component import Objective_Weight

### Inputs #################################################################################################################################################################################################

### Constants###
k_1 = 0.9                       # Constant ~0.90 - 0.95 - INPUT
A_load = 41.2*10**3             # Electric Loading [A/m] - INPUT
B_load = 0.88                   # Magnetic Loading [T] - INPUT
S_stress = 24.1*10**3           # Rated Shear Stress for UIUC Motor - INPUT

### Design Parameters###
#Power
P_out = 1.0 * 10**3             # Output Power [w] - INPUT
P_factor = 0.95                 # Power Factor [unitless] - INPUT
E = 0.95                        # Efficiency [unitless] - INPUT
pole_num = 20                   # Number of Poles - INPUT
#Dimensions
D_out = 0.337                   # Baseline Motor Outer Diameter [m] - INPUT
L_active = 0.2235               # Stack Length [m] - INPUT
D_ag = 0.277                    # Airgap Diameter [m] - INPUT
Heat_sink_in = 0.08128          # Baseline Heat Sink Inner Radius [m] - INPUT
Yoke_in = 0.1265                # Baseline Back Yoke Inner Radius [m] - INPUT
Windings_in = 0.1328            # Baseline Windings Inner Radius [m] - INPUT
Air_gap_in = 0.1384             # Baseline Airgap Inner Radius [m] - INPUT
Perm_mag_in = 0.1394            # Baseline Permanent Magnet Inner Radius [m] - INPUT
Titanium_in = 0.1519            # Baseline Titanium Shell Inner Radius [m] - INPUT
Carbon_fib_in = 0.1569          # Baseline Carbon Fiber Ring Inner Radius [m] - INPUT
Motor_out = 0.1697              # Baseline Motor Outer Radius [m] - INPUT
#Component Weights
Heat_sink_w = 6.168             # Weight of Heat Sink [kg] - INPUT
Yoke_w = 9.253                  # Weight of Yoke [kg] - INPUT
Windings_w = 6.3500             # Weight of Windings [kg] - INPUT
Perm_mag_w = 18.73              # Weight of Magnet [kg] - INPUT
Titanium_w = 12.551             # Weight of Titanium [kg] - INPUT
Carbon_fib_w = 4.941            # Weight of Carbon Fiber ring [kg] - INPUT
#Stray Weights
Ground_cyl_w = 3.130            # Ground Cylinar weight [kg] - INPUT
Bearing_w = 2.58                # Bearing weight [kg] - INPUT
Ground_ring_w = 0.454           # Ground ring Weight [kg] - INPUT
Lock_nut_w = 0.181              # Lock Nut Weight [kg]- INPUT 
Fan_w = 0.816                   # Fan Weight [kg] - INPUT
Stator_ring_w = 0.227           # Stator weight [kg] - INPUT
#Gearbox Parameters
K_gearbox = 72                  # Technology Level Scaling in Krantz Formula Factor [Unitless] - INPUT
Fan_RPM = 4000                  # Expected Fan Speed [RPM] - INPUT
#Tip Speed Limits
max_ts = 280                    # max allowed tip speed (0.75-0.8 Mach) [m/s] - INPUT
min_ts = 150                    # low end tip speed, common in conventional motor topologies (0.3 Mach) [m/s] - INPUT
#Aspect Ratios
# Thermal_AR_max = 0.942          # Max Thermal Aspect Ratio [unitless] *:) 6
# Thermal_AR_min = 0.157          # Min Thermal Aspect Ratio [unitless] *:) 1

Thermal_AR_max = 6          # Max Thermal Aspect Ratio [unitless] *:) 6
Thermal_AR_min = 1          # Min Thermal Aspect Ratio [unitless] *:) 1

LD_AR_max = 3.5                 # Max L/D Aspect Ratio [unitless]
LD_AR_min = 0.5                 # Min L/D Aspect Ratio [unitless]

### Parameters to Explore###
#Speed
n_min = 4                       # Min speed to explore [kRPM] - INPUT
n_max = 21                      # Max speed to explore [kRPM] - INPUT
#Dimensions
D_out_s_max = 0.6               # Max Outer Diameter to explore in algorithm [m] - INPUT
D_out_s_min = 0.15              # Min Outer Diameter to explore in algorithm [m] -  INPUT

### Conversions ############################################################################################################################################################################################

### Conversions ###
K_gearbox_metric = .454 * K_gearbox # Conversion factor from pounds to kg
HP_out = P_out*1.34102           # Convert Rated Output power to horsepower [HP] - INPUT 

### Diameter Ratios ###
D_ratio = D_ag/D_out                                                                    # Diameter ratio to keep constant [unitless]

### Volume Calculations ###
Vol = pi*(D_out/2)**2*L_active# Baseline Volume [m**3]
Heat_sink_vol = pi*(Yoke_in**2 - Heat_sink_in**2)*L_active                              # Heat Sink Volume [m**3]
Yoke_vol = pi*(Windings_in**2 - Yoke_in**2)*L_active                                    # Back Yoke Volume [m**3]
Windings_vol = pi*(Air_gap_in**2 - Windings_in**2)*L_active                             # Windings Volume [m**3]
Air_gap_vol = pi*(Perm_mag_in**2 - Air_gap_in**2)*L_active                              # Air Gap Volume [m**3]
Perm_mag_vol = pi*(Titanium_in**2 - Perm_mag_in**2)*L_active                            # Permanent Mag Volume [m**3]
Titanium_vol = pi*(Carbon_fib_in**2 - Titanium_in**2)*L_active                          # Titanium Volume [m**3]
Carbon_fib_vol = pi*(Motor_out**2 - Carbon_fib_in**2)*L_active                          # Carbon Fiber Volume [m**3]

### Weight Calculations ###
Region_w = Heat_sink_w+Yoke_w+Windings_w+Perm_mag_w+Titanium_w+Carbon_fib_w
Stray_w = Ground_cyl_w + Bearing_w + Ground_ring_w + Lock_nut_w + Fan_w + Stator_ring_w # Total Stray Weight [kg]
Motor_tot_w = Region_w + Stray_w

### Density Calculations ###
Heat_sink_d = Heat_sink_w/Heat_sink_vol                                                 # Heat Sink Density [kg/m**3]
Yoke_d = Yoke_w/Yoke_vol                                                                # Back Yoke Density [kg/m**3]
Windings_d = Windings_w/Windings_vol                                                    # Windings Density [kg/m**3]
Perm_mag_d = Perm_mag_w/Perm_mag_vol                                                    # Permanent Mag Density [kg/m**3]
Titanium_d = Titanium_w/Titanium_vol                                                    # Titanium Density [kg/m**3]
Carbon_fib_d = Carbon_fib_w/Carbon_fib_vol                                              # Carbon Fiber Density [kg/m**3]
Motor_Density = Motor_tot_w/Vol                                                         # Total material density of motor

### Scaling Calculations ###################################################################################################################################################################################

### Ranges to Explore ###
n = np.arange(n_min,n_max,1)*10**3                  # Operational Speeds of motor to explore [RPM]
n_sz = np.size(n)                                   # number of speeds to be tested [unitless]
D_out_s = np.arange(D_out_s_min,D_out_s_max, 0.005) # Outer Diameters to Explore [m]
D_out_s_sz = np.size(D_out_s)                       # Number of Outer Diameters Checked [unitless]

### Scaling Computations ###
D_ag_s = D_ratio*D_out_s                                    # Compute new Airgap Diameter based on ratio [m]
Vol_s = np.divide(P_out*60 * 1000,(pi**2*S_stress*n*E*P_factor))   # Calculate D**2*L [m**3]

### Ranges of Viable Design Space ###

#Tip Speed
D_ts_max = np.divide(max_ts*60, (pi*n)) # Max allowable Diameter due to tip speed [m] 
D_ts_min = np.divide(min_ts*60, (pi*n)) # Min allowable diameter due to tip speed [m]
#Aspect Ratio
tau_p = (pi*D_ag_s)/pole_num        # Pole Pitch [m]

L_T_AR_max = tau_p*Thermal_AR_max # Active lengths corresponding to max Thermal Aspect Ratio
L_T_AR_min = tau_p*Thermal_AR_min # Active lengths corresponding to min Thermal Aspect Ratio

L_LD_AR_max = D_out_s*LD_AR_max     # Active lengths corresponding to max L/D Aspect Ratio
L_LD_AR_min = D_out_s*LD_AR_min     # Active lengths corresponding to min L/D Aspect Ratio

### Region Diameters ###
D_out_ratio = D_out_s/D_out# Ratio of new to old diameter [unitless]
Heat_sink_in_s = Heat_sink_in * D_out_ratio     # Scaled Heat Sink Inner Radius [m]
Yoke_in_s = Yoke_in * D_out_ratio               # Scaled Back Yoke Inner Radius [m]
Windings_in_s = Windings_in * D_out_ratio       # Scaled Windings Inner Radius [m]
Air_gap_in_s = Air_gap_in * D_out_ratio         # Scaled Airgap Inner Radius [m]
Perm_mag_in_s = Perm_mag_in * D_out_ratio       # Scaled Permanent Magnet Inner Radius [m]
Titanium_in_s = Titanium_in * D_out_ratio       # Scaled Titanium Shell Inner Radius [m]
Carbon_fib_in_s = Carbon_fib_in * D_out_ratio   # Scaled Carbon Fiber Ring Inner Radius [m]
Motor_out_s = Motor_out * D_out_ratio           # Scaled Motor Outer Radius [m]


### Scaling Memory Preallocation ###
L_active_s = np.zeros((D_out_s_sz,n_sz))      # Scaled Active Length

Heat_sink_vol_s = np.zeros((D_out_s_sz,n_sz))   # Heat Sink Volume [m**3]
Yoke_vol_s = np.zeros((D_out_s_sz,n_sz))        # Back Yoke Volume [m**3]
Windings_vol_s = np.zeros((D_out_s_sz,n_sz))    # Windings Volume [m**3]
Air_gap_vol_s = np.zeros((D_out_s_sz,n_sz))     # Air Gap Volume [m**3]
Perm_mag_vol_s = np.zeros((D_out_s_sz,n_sz))    # Permanent Mag Volume [m**3]
Titanium_vol_s = np.zeros((D_out_s_sz,n_sz))    # Titanium Volume [m**3] 
Carbon_fib_vol_s = np.zeros((D_out_s_sz,n_sz))  # Carbon Fiber Volume [m**3]

Vol_cc = np.zeros((D_out_s_sz,n_sz))            # Volume Cross Check [m**3]

Heat_sink_w_s = np.zeros((D_out_s_sz,n_sz))     # Weight of Heat Sink [kg]
Yoke_w_s = np.zeros((D_out_s_sz,n_sz))          # Weight of Yoke [kg]
Windings_w_s = np.zeros((D_out_s_sz,n_sz))      # Weight of Windings [kg]
Perm_mag_w_s = np.zeros((D_out_s_sz,n_sz))      # Weight of Magnet [kg]
Titanium_w_s = np.zeros((D_out_s_sz,n_sz))      # Weight of Titanoim [kg]
Carbon_fib_w_s = np.zeros((D_out_s_sz,n_sz))    # Weight of Carbon Fiber ring [kg]

Stray_w_s = np.zeros((D_out_s_sz,n_sz))         # Scaled Stray Weight [kg]
Motor_tot_w_s = np.zeros((D_out_s_sz,n_sz))     # Total Scaled Weight [kg]

Thermal_AR = np.zeros((D_out_s_sz,n_sz))        # Thermal Aspect Ratio [unitless]

L_D_AR = np.zeros((D_out_s_sz,n_sz))            # L/D Aspect Ratio [unitless]
L_ts_max = np.zeros((n_sz,1))                   # Corresponding Length to Max allowable Diameter
L_ts_min = np.zeros((n_sz,1))                   # Corresponding Length to Min allowable Diameter

### RPM initializations ###
E_RPM = n                                                         # 'Motor RPM' in Krantz Formula - This is the faster speed input to the gearbox [RPM]
R_RPM = np.ones((n_sz, 1))*Fan_RPM                                # 'Rotor RPM' in Krantz Formula - This is the slower speed input to gearbox [RPM]

### Optimization ###########################################################################################################################################################################################
class Computational_Weight(Group):

    def setup(self):
        ### set up inputs
        indeps = self.add_subsystem("indeps", IndepVarComp())
        indeps.add_output("Motor_Density", Motor_Density, units = "kg / m**3", desc = "Volumetric Density of entire motor")
        indeps.add_output("P_out", P_out, units = "kW", desc = "Output power of motor in W")
        indeps.add_output("HP_out", HP_out, units = "hp", desc = "Output power of motor in HP")
        indeps.add_output("S_stress", S_stress, units = "Pa", desc = "Magnetic shear stress of motor")
        indeps.add_output("P_factor", P_factor, desc = "Power factor of motor")
        indeps.add_output("K_gearbox_metric", K_gearbox_metric, desc = "Technology level of gearbox")
        indeps.add_output("R_RPM", R_RPM[0], units = "rpm", desc = "Rotor RPM, slower gearbox speed")
        # indeps.add_output("var_speed", n_max * 10**3, units = "rpm", desc = "Motor speed, the value that will be varied by the optimizer")
        indeps.add_output("var_speed", 15 * 10**3, units = "rpm", desc = "Motor speed, the value that will be varied by the optimizer")

        ### create connections
        self.add_subsystem("combined_weight", Objective_Weight())
        self.connect("indeps.Motor_Density", "combined_weight.Motor_Density")
        self.connect("indeps.P_out", "combined_weight.P_out")
        self.connect("indeps.HP_out", "combined_weight.HP_out")
        self.connect("indeps.S_stress", "combined_weight.S_stress")
        self.connect("indeps.P_factor", "combined_weight.P_factor")
        self.connect("indeps.K_gearbox_metric", "combined_weight.K_gearbox_metric")
        self.connect("indeps.R_RPM", "combined_weight.R_RPM")
        self.connect("indeps.var_speed", "combined_weight.var_speed")

if __name__ == "__main__":

### OpenMDAO model #########################################################################################################################################################################################
    prob = Problem()
    prob.model = Computational_Weight()
    prob.model.add_design_var("indeps.var_speed", lower = n_min * 10**3, upper = n_max * 10**3)
    prob.model.add_objective("combined_weight.wt")
    
    prob.driver = ScipyOptimizeDriver()
    prob.driver.options["maxiter"] = 20000
    prob.driver.options["optimizer"] = "COBYLA"

    prob.setup()
    # prob.setup(force_alloc_complex = True)
    # prob.check_partials(compact_print = True, method = "cs")
    prob.run_driver()
    # prob.run_model()

    print("RPM: ", prob["indeps.var_speed"], "Combined Weight: ", prob["combined_weight.wt"]) #at 15,000 RPM, actual motor weight = 65.381 kg, gearbox weight from equation = 16.897 kg, total = 82.278 kg

### Map Calculations #######################################################################################################################################################################################

    check_data = [] #used for testing purposes only
    for y in np.arange(0, D_out_s_sz, 1):     # Sweep Airgap Diameter [m]

        for x in np.arange(0, n_sz, 1):       # Sweep Motor Operational Speeds [RPM]
    
            # Compute scaled length [m]
            L_active_s[y,x] = Vol_s[x]/(D_ag_s[y]**2)  
        
            # Compute scaled motor region volumes
        
            Heat_sink_vol_s[y,x] = pi*(Yoke_in_s[y]**2 - Heat_sink_in_s[y]**2)*L_active_s[y,x]      # Heat Sink Volume [m**3]
            Yoke_vol_s[y,x] = pi*(Windings_in_s[y]**2 - Yoke_in_s[y]**2)*L_active_s[y,x]            # Back Yoke Volume [m**3]
            Windings_vol_s[y,x] = pi*(Air_gap_in_s[y]**2 - Windings_in_s[y]**2)*L_active_s[y,x]     # Windings Volume [m**3]
            Air_gap_vol_s[y,x] = pi*(Perm_mag_in_s[y]**2 - Air_gap_in_s[y]**2)*L_active_s[y,x]      # Air Gap Volume [m**3]
            Perm_mag_vol_s[y,x] = pi*(Titanium_in_s[y]**2 - Perm_mag_in_s[y]**2)*L_active_s[y,x]    # Permanent Mag Volume [m**3]
            Titanium_vol_s[y,x] = pi*(Carbon_fib_in_s[y]**2 - Titanium_in_s[y]**2)*L_active_s[y,x]  # Titanium Volume [m**3]
            Carbon_fib_vol_s[y,x] = pi*(Motor_out_s[y]**2 - Carbon_fib_in_s[y]**2)*L_active_s[y,x]  # Carbon Fiber Volume [m**3]
        
            # Cross Check Volume Scaling [m**3]
        
            Vol_cc[y,x] =  pi*(Motor_out_s[y])**2*L_active_s[y,x]
                    
            # Scaled Weight Calculations
        
            Heat_sink_w_s[y,x]= Heat_sink_vol_s[y,x]*Heat_sink_d     # Scaled Weight of Heat Sink [kg]
            Yoke_w_s[y,x] = Yoke_vol_s[y,x]*Yoke_d                   # Scaled Weight of Yoke [kg]
            Windings_w_s[y,x] = Windings_vol_s[y,x]*Windings_d       # Scaled Weight of Windings [kg]
            Perm_mag_w_s[y,x] = Perm_mag_vol_s[y,x]*Perm_mag_d       # Scaled Weight of Magnet [kg]
            Titanium_w_s[y,x] = Titanium_vol_s[y,x]*Titanium_d       # Scaled Weight of Titanoim [kg]
            Carbon_fib_w_s[y,x] = Carbon_fib_vol_s[y,x]*Carbon_fib_d # Scaled Weight of Carbon Fiber ring [kg]
        
            Stray_w_s[y,x] = (Vol_cc[y,x]/Vol)*Stray_w  # Scaled Stray Weight [kg]
        
            # Motor Total Scaled Weight [kg]
        
            Motor_tot_w_s[y,x] = Heat_sink_w_s[y,x]+Yoke_w_s[y,x]+Windings_w_s[y,x]+ Perm_mag_w_s[y,x]+Titanium_w_s[y,x]+Carbon_fib_w_s[y,x]+Stray_w_s[y,x]
                   
            # Compute Thermal Aspect Ratio [Unitless]
        
            Thermal_AR[y,x] = L_active_s[y,x]/tau_p[y] 
        
            # Compute L/D Aspect Ratio [Unitless]
        
            L_D_AR[y,x] = L_active_s[y,x]/D_out_s[y]
        
            # Compute Rotor Tip Speed Limits
        
            L_ts_max[x] = Vol_s[x]/((D_ts_max[x]*D_ratio)**2) # Corresponding Length to Max allowable Diameter
            L_ts_min[x] = Vol_s[x]/((D_ts_min[x]*D_ratio)**2) # Corresponding Length to Min allowable Diameter
            #the loop below is for testing purposes only
            if y == 4:
                check_data.append(Motor_tot_w_s[y, x])


    
### Gearbox Weight Calculations ############################################################################################################################################################################

    Gearbox_index = np.divide((np.power(HP_out,0.76)*np.power(E_RPM,0.13)),(np.power(R_RPM,0.89)))   # 'Index' in Krantz Formula
    Gearbox_w = K_gearbox*Gearbox_index                               # Gearbox weight [lb]
    Gearbox_w_kg = Gearbox_w*0.4535                                   # Gearbox weight [kg]

### Motor + Gearbox Weight #################################################################################################################################################################################

    Drive_System_w_s = Motor_tot_w_s[0,:] + Gearbox_w # total weight of drive system [kg]


### Plots ##################################################################################################################################################################################################

### Stack Length vs. Outer Diameter Plot (No Constraint Lines)
    plt.figure(0)
    plt.plot(L_active_s, D_out_s)

    plt.xlabel('Stack Length, m')
    plt.ylabel('Outer Diameter, m')
    plt.legend(["%d RPM" % rpm for rpm in n])

### Stack Length vs. Outer Diameter Plot (With Constraint Lines)

    plt.figure(1)

    plt.plot(L_active_s, D_out_s, linewidth=1.25)
    plt.plot(L_ts_max, D_ts_max, ':k', linewidth= 2.5)
    plt.plot(L_ts_min, D_ts_min, ':k', linewidth= 2.5)
    plt.plot(L_T_AR_max, D_out_s, '--k', linewidth= 1.75)
    plt.plot(L_LD_AR_min, D_out_s, '-.k', linewidth= 1.75)

    plt.xlabel('Stack Length, m')
    plt.ylabel('Outer Diameter, m')

    axes = plt.gca()
    axes.set_xlim([0.00,2.10])
    axes.set_ylim([0.14,0.61])

    plt.legend(["%d RPM" % rpm for rpm in n])

### Weight vs. Speed Plot (Just Motor)

    plt.figure(2)

    plt.plot(n, Motor_tot_w_s[1,:],'b', linewidth=2)

    plt.xlabel('Motor Operating Speed, RPM')
    plt.ylabel('Weight, kg')

    plt.legend(['Motor Weight'])


## Weight vs. Speed Plot (Motor, Gearbox, and Combined Weights)

    plt.figure(3)

    plt.plot(n, Drive_System_w_s[1,:],'o')#dots for theoretical drive systems
    mySum = np.add(Gearbox_w_kg[1, :], Motor_tot_w_s[1, :])

    plt.plot(n, Drive_System_w_s[1,:], linewidth= 2)#line for 1MW power trend line
    plt.plot(n, Gearbox_w_kg[1,:], linewidth= 2)#gearbox wt
    plt.plot(n, Motor_tot_w_s[1,:],'b', linewidth= 2)#motor weight
    plt.plot(n, mySum, linewidth = 2)#total weight
    plt.plot(prob["indeps.var_speed"], prob["combined_weight.wt"], "o", color = "red")#optimizer returned answer

    plt.xlabel('Motor Operating Speed, RPM')
    plt.ylabel('Weight, kg')

    plt.legend(['Theoretical Drive Systems', '1MW Power Trend Line', 'Gearbox Weight', 'Motor Weight', "Total Assembly Weight", "Optimizer's Total Assembly Weight"])
    plt.show()
