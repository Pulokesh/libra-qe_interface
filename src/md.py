#*********************************************************************************
#* Copyright (C) 2016 Ekadashi Pradhan, Kosuke Sato, Alexey V. Akimov
#*
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 2 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/

## \file md.py
# This module implements the functions which execute classical MD.
#
import os
import sys
import math

# First, we add the location of the library to test to the PYTHON path
sys.path.insert(1,os.environ["libra_mmath_path"])
sys.path.insert(1,os.environ["libra_chemobjects_path"])
sys.path.insert(1,os.environ["libra_hamiltonian_path"])
sys.path.insert(1,os.environ["libra_dyn_path"])

from libmmath import *
from libchemobjects import *
from libhamiltonian import *
from libdyn import *
from LoadPT import * 
from exe_espresso import*
from unpack_file import*
from libra_to_espresso import*

##############################################################

def run_MD(syst,data,params,cell_dm):
    ##
    # Finds the keywords and their patterns and extracts the parameters
    # \param[in,out] syst System object that includes atomic system information.
    # \param[in,out] el   The list of the objects containig electronic DOFs for the nuclear coordinate
    #                     given by syst, but may correspond to differently-prepared coherent
    # wavefunctions (different superpositions or sampling over the wfc phase, initial excitations).
    # Under CPA, the propagation of several such variables corresponds to the same nuclear dynamics,
    # we really don't need to recompute electronic structure for each one, which can be used to 
    # accelerate the computations. Now, if you want to go beyond CPA - just use only one object in
    # the el list and run several copies of the run_MD function to average over initial conditions.
    # Also note that even under the CPA, we need to run this function several times - to sample
    # over initial nuclear distribution
    # \param[in,out] data Data extracted from QE output file, in the dictionary form.
    # \param[in,out] params Input data containing all manual settings and some extracted data.
    # \param[out] test_data  the output data for debugging, in the form of dictionary

    # This function executes classical MD in Libra and electronic structure calculation
    # in Quantum Espresso iteratively.
    #
    # Used in:  main.py/main
    # Open and close energy and trajectory files - this will effectively 
    # make them empty (to remove older info, in case we restart calculations)
    fe = open(params["ene_file"],"w")
    fe.close()
    ft = open(params["traj_file"],"w")
    ft.close()
    
    dt_nucl = params["dt_nucl"]
    Nsnaps = params["Nsnaps"]
    Nsteps = params["Nsteps"]

    # Create a variable that will contain propagated nuclear DOFs
    mol = Nuclear(3*syst.Number_of_atoms)
    syst.extract_atomic_q(mol.q)
    syst.extract_atomic_p(mol.p)
    syst.extract_atomic_f(mol.f)
    syst.extract_atomic_mass(mol.mass)

    # Rydberg to Hartree conversion factor
    Ry_to_Ha = 0.5
    MD_type = params["MD_type"]
    kB = 3.1668e-6 # Boltzmann constant in a.u.

    # initialize Thermostat object
    if MD_type == 1: # NVT-MD
        print " Initialize thermostats......"
        therm = Thermostat({"nu_therm":params["nu_therm"], "NHC_size":params["NHC_size"], "Temperature":params["Temperature"], "thermostat_type":params["thermostat_type"]})
        therm.set_Nf_t(3*syst.Number_of_atoms)
        therm.set_Nf_r(0)
        therm.init_nhc()

    # Run actual calculations
    for i in xrange(Nsnaps):

        for j in xrange(Nsteps):

            if MD_type == 1: # NVT-MD
                # velocity scaling
                for k in xrange(3*syst.Number_of_atoms):
                    mol.p[k] = mol.p[k] * therm.vel_scale(0.5*dt_nucl)

            # >>>>>>>>>>> Nuclear propagation starts <<<<<<<<<<<<
            mol.propagate_p(0.5*dt_nucl)
            mol.propagate_q(dt_nucl) 
            libra_to_espresso(data, params, mol, cell_dm)
            exe_espresso(params)         
            E, Grad, data = unpack_file(params["qe_out"], cell_dm)
            epot = Ry_to_Ha*E    # total energy from QE, the potential energy acting on nuclei

            # Ry/au unit of Force in Quantum espresso
            # So, converting Rydberg to Hartree
            for k in xrange(syst.Number_of_atoms):
                mol.f[3*k]   = Ry_to_Ha*Grad[k][0]
                mol.f[3*k+1] = Ry_to_Ha*Grad[k][1]
                mol.f[3*k+2] = Ry_to_Ha*Grad[k][2]

            ekin = compute_kinetic_energy(mol)

            # Propagate Thermostat
            if MD_type == 1:
                therm.propagate_nhc(dt_nucl, ekin, 0.0, 0.0)

            mol.propagate_p(0.5*dt_nucl)
            # >>>>>>>>>>> Nuclear propagation ends <<<<<<<<<<<<
#            ekin = compute_kinetic_energy(mol)

            if MD_type == 1: # NVT-MD
                # velocity scaling
                for k in xrange(3*syst.Number_of_atoms):
                    mol.p[k] = mol.p[k] * therm.vel_scale(0.5*dt_nucl)


            t = dt_nucl*(i*Nsteps + j) # simulation time in a.u.
        ################### Printing results ############################
# >>>>>>>>>>>>>> Compute energies <<<<<<<<<<<<<<<<<<<<<<<<<
        ekin = compute_kinetic_energy(mol)
        etot = ekin + epot

        ebath = 0.0
        if MD_type == 1:
            ebath = therm.energy()

        eext = etot + ebath
        curr_T = 2.0*ekin/(3*syst.Number_of_atoms*kB)

        ################### Printing results ############################

        # Energy
        fe = open(params["ene_file"],"a")
        fe.write("i= %3i ekin= %8.5f  epot= %8.5f  etot= %8.5f  eext = %8.5f curr_T= %8.5f\n" % (i, ekin, epot, etot, eext, curr_T)) 
        syst.set_atomic_q(mol.q)
        syst.print_xyz(params["traj_file"],i)
        fe.close()
    # input test_data for debugging
    test_data = {}

    return test_data

def init_system(data, g, T):
    ##
    # Finds the keywords and their patterns and extracts the parameters
    # \param[in] data   The list of variables, containing atomic element names and coordinates
    # \param[in] g      The list of gradients on all atoms
    # This function returns System object which will be used in classical MD.
    #
    # Used in:  main.py/main

    # Create Universe and populate it
    Ry_to_Ha = 0.5
    U = Universe();   Load_PT(U, "elements.txt", 0)

    syst = System()

    sz = len(data["coor_atoms"])
    for i in xrange(sz):
        atom_dict = {} 
        atom_dict["Atom_element"] = data["l_atoms"][i]

        # warning: below we take coordinates in Angstroms, no need for conversion here - it will be
        # done inside
        atom_dict["Atom_cm_x"] = data["coor_atoms"][i][0]
        atom_dict["Atom_cm_y"] = data["coor_atoms"][i][1]
        atom_dict["Atom_cm_z"] = data["coor_atoms"][i][2]

        print "CREATE_ATOM ",atom_dict["Atom_element"]
        at = Atom(U, atom_dict)
        at.Atom_RB.rb_force = VECTOR(Ry_to_Ha*g[i][0], Ry_to_Ha*g[i][1], Ry_to_Ha*g[i][2])

        syst.CREATE_ATOM(at)

    syst.show_atoms()

    print "Number of atoms in the system = ", syst.Number_of_atoms
    # Initialize random velocity at T(K) using normal distribution
    syst.init_atom_velocities(T)

    return syst



