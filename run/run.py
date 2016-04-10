import os
import sys
import math


user = 0  # 0 - Alexey, 1 - Ekadashi

################ System-specific settings ########################
if user==0:
    # For Alexey
    libra_bin_path = "/projects/academic/alexeyak/alexeyak/libra-dev/libracode-code/_build/src" # set the path name to the source files in libracode
    libra_qe_int_path = "/user/alexeyak/Programming/libra-qe_interface/src"
    res_dir =  "/user/alexeyak/Programming/libra-qe_interface/run/res/"

elif user==1:
    # For Ekadashi
    libra_bin_path = "/projects/academic/alexeyak/ekadashi/libracode-dev/libracode-code/_build/src"
    libra_qe_int_path = "/projects/academic/alexeyak/ekadashi/devel/libra-qe_interface/src"
    res_dir = "/projects/academic/alexeyak/ekadashi/devel/libra-qe_interface/run/res/"


os.environ["src_path"] = libra_qe_int_path   # Path to the source code
sys.path.insert(1,os.environ["src_path"])    # Path to the source code

from path_libra_lib import * # import path_libra_lib module
path_libra_lib(libra_bin_path)               # Path to the libra libraries

import main # import main module of the libra-QE-interface code



########## Setup all manual parameters here ####################

params = {}

#params["no_ex"] = 2  #number of excited states
#params["nband"] = 12 #total number of orbitals
#params["HOMO"] = 6   #orbital number of HOMO
params["qe_debug_print"] = 1

for i in range(0,params["no_ex"]):
    params["qe_inp0%i" %i] = "x%i.scf.in" %i    # initial input file
    params["qe_inp%i" %i] = "x%i.scf_wrk.in" %i # working input file 
    params["qe_out%i" %i] = "x%i.scf.out" %i    # output file

params["nproc"] = 1              # the number of processors
params["dt_nucl"]=20.0  # time step for nuclear dynamics  ex) 20 a.u. = 0.5 fsec
params["Nsnaps"]=5      # the number of MD rounds
params["Nsteps"]=1      # the number of MD steps per snap
params["res"]=res_dir   # the directory where the energies and NACs files will be printed out
params["traj_file"] = params["res"]+"md.xyz"
params["ene_file"] = params["res"]+"ene.dat"

params["MD_type"] = 1  # NVT ensamble
#params["MD_type"] = 0  # NVE ensamble

# Thermostat parameters
params["Temperature"] = 300.0
params["nu_therm"] = 0.01
params["NHC_size"] = 3
params["thermostat_type"] = "Nose-Hoover"

########### Now start actual calculations ###########################

#main.main(params)  # run actual calculations
sys.path.insert(1,os.environ["libra_hamiltonian_path"] + "/Hamiltonian_Atomistic/Hamiltonian_QM/Control_Parameters")
from libcontrol_parameters import *

params["excitations"] = [ excitation(0,1,0,1), excitation(0,1,1,1) ] 

data, test_data = main.main(params)  # run actual calculations

