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
## \file hamiltonian_vib.py
# This module implements the function which creates and updates ham_vib vibronic hamiltonian object.

import os
import sys
import math

from states import *

if sys.platform=="cygwin":
    from cyglibra_core import *
elif sys.platform=="linux" or sys.platform=="linux2":
    from liblibra_core import *


def compute_Hvib(H_el,NAC):
    ##
    # Compute the vibronic Hamiltonian
    # \param[in] H_el Electronic Hamiltonian matrix (diagonal) - of type MATRIX: nstates x nstates
    # \param[in] NAC Nonadiabatic couplings matrix - of type CMATRIX: nstates x nstates
    # H_vib - returned CMATRIX bound for vibronic hamiltonian 

    # Here, nstates - is the number of excited states included into consideration
    # Assume atomic units: hbar = 1

    nstates = H_el.num_of_cols

    H_vib = CMATRIX(nstates,nstates)

    for i in xrange(nstates):
            H_vib.set(i,i,H_el.get(i,i))

    for i in xrange(nstates):
        for j in xrange(nstates):
            if j != i:
                H_vib.set(i,j,(-1.0j+0.0)*NAC.get(i,j))

    return H_vib




def update_vibronic_hamiltonian(ham_el, ham_vib, params,E_SD,nac,suffix, opt):
    ##
    #
    # This function transforms the 1- or N- electron energies matrix and the matrix of 
    # nonadiabatic couplings into the matrix of excitation energies and corresponding couplings
    # between the considered excited Slater determinants (SD). In doing this, it will return 
    # the vibronic and electronic (in SD basis) Hamiltonians.
    # 
    # \param[in,out]     ham_el Electronic (adiabatic) Hamiltonian (MATRIX)
    # \param[in,out]     ham_vib Vibronic Hamiltonian (CMATRIX)
    # \param[in] params  contains the dictionary of the input parameters from {gms,qe}_run.py
    # \param[in] E_SD    total excitation energy (MATRIX) 
    ##### \param[in] E_mol_red   the matrix of the 1-electron MO energies, in reduced space (MATRIX)
    # \param[in] nac   the matrix of the NACs computed with the 1-electon MOs, in reduced space (CMATRIX)
    # \param[in] suffix the suffix to add to the file names for the files created in this function
    # \param[in] opt The option that defines what kind of electronic approximation has been utilized
    #            opt == 0 - 1-electron (KS, similar to original Pyxaid), in this case nac is typically 
    #            a real matrix
    #            opt == 1 (or any other value) - N-electron (SD, multielectronic wavefunction), in this case
    #            nac may be a complex
    #
    # This function does not return anything - it merely modifies the already existing matrices
    # VERY IMPORTANT: we should modify the existing matrices (bound to the hamiltonian object), not
    # create the new ones. In the latter case we loose the binding of the previousely allocated 
    # matrices with the hamiltonian object!!!
    #
    # Used in: md.py/run_MD

    HOMO = params["HOMO"]
    min_shift = params["min_shift"]
    max_shift = params["max_shift"]

    states = params["excitations"]
    nstates = len(states)  
    H_el = MATRIX(nstates,nstates)  # electronic Hamiltonian
    D_el = CMATRIX(nstates,nstates)  # nonadiabatic couplings
    flag = params["print_sd_ham"]

    # Excitation energy : 
    # ex) GS = (0,1,0,1) -> E_GS = 0
    #     SE0 = (0,1,1,1) -> E_SE0 = E(LUMO) - E(HOMO)
    #     SE1 = (-1,1,1,1) -> E_SE1 = E(LUMO) - E(HOMO-1) 
    #     etc ........

    # E.g. 
    # HOMO = 3, min_shift = -1, max_shift = 1
    # [0,1,2,3,4,5,6,7]  <- original set
    #     [0,1,2]        <- reduced set
    #

    pyx_st = pyxaid_states(states, min_shift, max_shift)

    #============ EX energies ===============    
    for i in xrange(nstates):

        #h_indx = states[i].from_orbit[0] - min_shift  # index of the hole orbital w.r.t. the lowest included in the active space orbital
        #e_indx = states[i].to_orbit[0] - min_shift  # --- same, only for the electron orbital

        #EX_ene = E_mol_red.get(e_indx,e_indx) - E_mol_red.get(h_indx,h_indx) # excitation energy

        # ************* Here, H_el only imports E_SD info.********************** 
        H_el.set(i,i,E_SD.get(i,i))
        ham_el.set(i,i,E_SD.get(i,i))
        ham_vib.set(i,i,E_SD.get(i,i), 0.0)
        #***********************************************************************

        #H_el.set(i,i,EX_ene)
        #ham_el.set(i,i,EX_ene)
        #ham_vib.set(i,i,EX_ene, 0.0)

        #if flag==1:
        #    print "excitation ", i, " h_indx = ", h_indx, " e_indx = ", e_indx, " EX_ene = ", EX_ene
        #    print "source orbital energy = ",E_mol_red.get(h_indx,h_indx)
        #    print "target orbital energy = ",E_mol_red.get(e_indx,e_indx)


    #============== Couplings =================
    print "Do couplings"
     
    for I in xrange(nstates):
        for J in xrange(nstates):

            if I != J:
                st_I = Py2Cpp_int(pyx_st[I])
                st_J = Py2Cpp_int(pyx_st[J])
                print "st_I= ", pyx_st[I] # show_vector(st_I)
                print "st_J= ", pyx_st[J] # show_vector(st_J)

                if opt == 0: # 1-electron approximation - then need to transform KS couplings
                             # into SD space

                    coupled,a,b = delta(st_I, st_J)
                    print "delta returns ", coupled, a, b
            
                    if coupled:
                        i = abs(a) - 1
                        j = abs(b) - 1
                        print "pair of SD (",I,",",J,") is coupled via orbitals(in reduced space) ", i,j 
                        D_el.set(I,J,(-1.0j+0.0)*nac.get(i,j))
                        ham_vib.set(I,J,(-1.0j+0.0)*nac.get(i,j))
                    else:
                        D_el.set(I,J, 0.0, 0.0)
                        ham_vib.set(I,J, 0.0, 0.0)
                    print "\n"

                else:  # N-electron approximation - coupling is alreay there
                    D_el.set(I,J, (-1.0j+0.0)*nac.get(I,J))
                    ham_vib.set(I,J,(-1.0j+0.0)*nac.get(I,J))
                    print "\n"
      
    if params["print_sd_ham"] == 1:
        ham_vib.real().show_matrix(params["sd_ham"] + "Ham_vib_re_" + suffix)
        ham_vib.imag().show_matrix(params["sd_ham"] + "Ham_vib_im_" + suffix)
        # ********** "CMATRIX.show_matrix(filename)" is not exported from Libra
        # **********  now it is commented out

    # Returned values - actually we just update matrices ham_el and ham_vib 
    # 
    # !!! Don't create new instances (new MATRIX and CMATRIX objects) 
    #
    # ham_el - electronic Hamiltonian - the real diagonal matrix with adiabatic energies of the states
    #         w.r.t the ground state energy
    # ham_vib - vibronic Hamiltonian - the complex-valued matrix, also containing nonadiabatic couplings
    # on the off-diagonals   
