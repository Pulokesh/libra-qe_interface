#*********************************************************************************
#* Copyright (C) 2015 Kosuke Sato, Alexey V. Akimov
#*
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 2 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/

## \file nve.py
# This module implements the functions which execute classical MD.
# 
# Used in : main.py/


#from create_gamess_input import *
from create_espresso_input import *
#from create_pdb_file import *
#from exe_gamess import *
#from gamess_to_libra import *
from espresso_to_libra import *

import os
import sys
import math

# Fisrt, we add the location of the library to test to the PYTHON path
cwd = "/projects/academic/alexeyak/alexeyak/libra-dev/libracode-code"
print "Current working directory", cwd
sys.path.insert(1,cwd+"/_build/src/mmath")
sys.path.insert(1,cwd+"/_build/src/chemobjects")
sys.path.insert(1,cwd+"/_build/src/hamiltonian")
sys.path.insert(1,cwd+"/_build/src/dyn")
#sys.path.insert(1,cwd+"/../../_build/src/hamiltonian/hamiltonian_atomistic")

print "\nTest 1: Importing the library and its content"
from libmmath import *
from libchemobjects import *
from libhamiltonian import *
from libdyn import *
#from cyghamiltonian_atomistic import *
from LoadPT import * # Load_PT

##############################################################

def exe_espresso(params):
    ##
    # This is a function that call QE execution on the compute node
    # \param[in] params Input data containing all manual settings and some extracted data.
    #

    pw_exe = params["pw_exe"]
    inp = params["qe_inp"]
    out = params["qe_out"]
    nproc = params["nproc"]
    scr_dir = params["scr_dir"]
    os.system("srun %s -n %s < %s > %s" % (pw_exe,nproc,inp,out))



def run_MD(syst,ao,E,C,data,params):
    ##
    # Finds the keywords and their patterns and extracts the parameters
    # \param[in] syst   System object that includes atomic system information.
    # \param[in] ao     Atomic orbital basis
    # \param[in] E      Molecular orbital energies
    # \param[in] C      MO-LCAO coefficients
    # \param[in] data   Data extracted from GAMESS output file, in the dictionary form.
    # \param[in] params Input data containing all manual settings and some extracted data.
    # This function executes classical MD in Libra and electronic structure calculation
    # in GAMESS iteratively.
    #
    # Used in:  main.py/main/nve


    # Open and close energy and trajectory files - this will effectively 
    # make them empty (to remove older info, in case we restart calculations)
    fe = open(params["ene_file"],"w")
    fe.close()

    ft = open(params["traj_file"],"w")
    ft.close()
    
    dt = params["dt_nucl"]
    Nsnaps = params["Nsnaps"]
    Nsteps = params["Nsteps"]


    # Create a variable that will contain propagated nuclear DOFs
    mol = Nuclear(3*syst.Number_of_atoms)
    syst.extract_atomic_q(mol.q)
    syst.extract_atomic_p(mol.p)
    syst.extract_atomic_f(mol.f)
    syst.extract_atomic_mass(mol.mass)

    # Debug printing
    for i in xrange(syst.Number_of_atoms):
        print "mass m=",mol.mass[3*i], mol.mass[3*i+1], mol.mass[3*i+2]
        print "coordinates q = ", mol.q[3*i], mol.q[3*i+1], mol.q[3*i+2]
        print "momenta p= ", mol.p[3*i], mol.p[3*i+1], mol.p[3*i+2]
        print "forces f= ",  mol.f[3*i], mol.f[3*i+1], mol.f[3*i+2]
        print "********************************************************"


    # Run actual calculations
    for i in xrange(Nsnaps):

        syst.set_atomic_q(mol.q)
        syst.print_xyz(params["traj_file"],i)

        for j in xrange(Nsteps):

            ij = i*Nsteps + j
            mol.propagate_p(0.5*dt)
            mol.propagate_q(dt) 
          
            # ======= Compute forces and energies using GAMESS ============
            write_qe_inp(data, params, mol)
            exe_espresso(params)         
)            
            Grad, data = espresso_to_libra(params, ij) # this will update AO and gradients

            epot = data["tot_ene"]         # total energy from QE
            for k in xrange(syst.Number_of_atoms):
                mol.f[3*k]   = -Grad[k][0]
                mol.f[3*k+1] = -Grad[k][1]
                mol.f[3*k+2] = -Grad[k][2]

            mol.propagate_p(0.5*dt)

            ekin = compute_kinetic_energy(mol)
       
            t = dt*ij # simulation time in a.u.
            fe = open(params["ene_file"],"a")
            fe.write("i= %3i ekin= %8.5f  epot= %8.5f  etot= %8.5f\n" % (i, ekin, epot, ekin+epot)) 
            fe.close()


def init_system(data, g):
    ##
    # Finds the keywords and their patterns and extracts the parameters
    # \param[in] data   The list of variables, containing atomic element names and coordinates
    # \param[in] g      The list of gradients on all atoms
    # This function returns System object which will be used in classical MD.
    #
    # Used in:  main.py/main/nve


    # Create Universe and populate it
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
        at.Atom_RB.rb_force = VECTOR(-g[i][0], -g[i][1], -g[i][2])

        syst.CREATE_ATOM(at)

    syst.show_atoms()
    print "Number of atoms in the system = ", syst.Number_of_atoms

    return syst



