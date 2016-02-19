#*********************************************************************************
#* Copyright (C) 2016 Kosuke Sato, Alexey V. Akimov
#*
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 2 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/

## \create_gamess_input.py
#  This module defines the functions to create a GAMESS input files as JOB.inp.


import os
import sys
import math

# Fisrt, we add the location of the library to test to the PYTHON path
cwd = "/projects/academic/alexeyak/alexeyak/libra-dev/libracode-code"
#print "Current working directory", cwd
sys.path.insert(1,cwd+"/_build/src/mmath")
sys.path.insert(1,cwd+"/_build/src/chemobjects")
sys.path.insert(1,cwd+"/_build/src/hamiltonian")
sys.path.insert(1,cwd+"/_build/src/dyn")
#sys.path.insert(1,cwd+"/../../_build/src/hamiltonian/hamiltonian_atomistic")

#print "\nTest 1: Importing the library and its content"
from libmmath import *
from libchemobjects import *
from libhamiltonian import *
from libdyn import *
#from cyghamiltonian_atomistic import *


def read_gms_inp_templ(inp_filename):
    ##
    # Finds the keywords and their patterns and extracts the parameters
    # \param[in] inp_filename : The name of GAMESS input file used as template
    # This function returns the format of GAMESS information before 
    # coordinates of atoms.
    #
    # Used in:  main.py/main/initial_gamess_exe    

    f = open(inp_filename,"r")
    templ = f.readlines()
    f.close()

    N = len(templ)
    for i in range(0,N):
        s = templ[i].split()
        if len(s) > 0 and s[0] == "$DATA":
            ikeep = i + 2
            break

    templ[ikeep+1:N] = []

    return templ
    

def write_gms_inp(data, params, mol):
    ##
    # Finds the keywords and their patterns and extracts the parameters
    # \param[in] l_atoms   A list of atoms
    # \param[in] l_charges A list of atomic charges
    # \param[in] l_gam_for includes the template of GAMESS input file 
    # \param[in] mol The object containing nuclear DOF
    # \param[in] inp_filename The name of GAMESS input file
    # This function returns the GAMESS input file
    #
    # Used in:  main.py/main/nve/nve_MD

    gms_inp_templ = params["gms_inp_templ"]
    gms_inp = params["gms_inp"]

    B_to_A = 0.529177208 # Bohr to Angstrom
    g = open(gms_inp,"w")

    # Print the control section
    sz = len(gms_inp_templ)
    for i in xrange(sz):
        g.write(gms_inp_templ[i])

    # Important: Blank line
    g.write("\n")

    # Print coordinates
    Natoms = len(data["l_atoms"])
    for i in xrange(Natoms):
        elt = data["l_atoms"][i]
        q = data["l_charges"][i]
        x = B_to_A*mol.q[3*i] 
        y = B_to_A*mol.q[3*i+1]
        z = B_to_A*mol.q[3*i+2]
        g.write("%s   %2.1f    %12.7f    %12.7f    %12.7f  \n"  % (elt, q, x, y, z) )

    g.write(" $END \n")
    g.close()


    
