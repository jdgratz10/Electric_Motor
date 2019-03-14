from math import pi

############ The following is the keywords input to the regression model for motor weight calculation ############
keywords = ["Axial", "Aero", "OutRunner", "LiquidCool"] # user input specifies what keyword to use. Must be a list, even if there is only one keyword

############ The following is the necessary inputs for motor weight calculation in the computational model ############

### Constant Values ###

#Physical Constants
S_stress = 24.1*10**3   # Rated Shear Stress for UIUC Motor
P_factor = 0.95 # Power Factor [unitless] 
K_gearbox = 72  # Technology Level Scaling in Krantz Formula Factor [Unitless] 
K_gearbox_metric = .454 * K_gearbox # Conversion factor from pounds to kg
prop_RPM = 4000 # Expected propeller Speed [RPM] 
#Dimensions
D_out = 0.337   # Baseline Motor Outer Diameter [m]
L_active = 0.2235   # Stack Length [m] 
#Component Weights
Heat_sink_w = 6.168 # Weight of Heat Sink [kg] 
Yoke_w = 9.253  # Weight of Yoke [kg] 
Windings_w = 6.3500 # Weight of Windings [kg] 
Perm_mag_w = 18.73  # Weight of Magnet [kg] 
Titanium_w = 12.551 # Weight of Titanium [kg] 
Carbon_fib_w = 4.941    # Weight of Carbon Fiber ring [kg] 
#Stray Weights
Ground_cyl_w = 3.130    # Ground Cylinar weight [kg] 
Bearing_w = 2.58    # Bearing weight [kg] 
Ground_ring_w = 0.454   # Ground ring Weight [kg] 
Lock_nut_w = 0.181  # Lock Nut Weight [kg]
Fan_w = 0.816   # Fan Weight [kg] 
Stator_ring_w = 0.227   # Stator weight [kg]

### Calculations ###

#Volume Calculation
Vol = pi*(D_out/2)**2*L_active  # Baseline Volume [m**3]
#Weight Calculations
Region_w = Heat_sink_w+Yoke_w+Windings_w+Perm_mag_w+Titanium_w+Carbon_fib_w # Total Region Weight [kg]
Stray_w = Ground_cyl_w + Bearing_w + Ground_ring_w + Lock_nut_w + Fan_w + Stator_ring_w # Total Stray Weight [kg]
Motor_tot_w = Region_w + Stray_w    # Total Motor Weight [kg]

#Density Calculation
Motor_Density = Motor_tot_w/Vol # Total material density of motor



