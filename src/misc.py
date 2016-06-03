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

## \file gamess_to_libra.py
# This module implements the functions that extract parameters from the gamess output file:
# atomic forces , molecular energies, molecular orbitals, and atomic basis information.
# The forces are used for simulating Classical MD on Libra
# and the others for calculating time-averaged energies and Non-Adiabatic Couplings(NACs).

import os
import sys
import math

if sys.platform=="cygwin":
    from cyglibra_core import *
elif sys.platform=="linux" or sys.platform=="linux2":
    from liblibra_core import *


def reduce_matrix(M,min_shift,max_shift,HOMO_indx):
    ##
    # Extracts a sub-matrix M_sub of the original matrix M. The size of the extracted matrix is
    # controlled by the input parameters
    # \param[in] M The original input matrix
    # \param[in] min_shift - is the index defining the minimal orbital in the active space
    # to consider. This means that the lowest 1-electron state will be HOMO_indx + min_shift.
    # \param[in] max_shift - is the index defining the maximal orbital in the active space
    # to consider. This means that the highest 1-electron state will be HOMO_indx + max_shift.
    # \param[in] HOMO_indx - the index of the HOMO orbital (indexing starts from 0)
    # Example: if we have H2O system - 8 valence electrons, so 4 orbitals are occupied:
    # occ = [0,1,2,3] and 2 more states are unoccupied virt = [4,5] Then if we
    # use HOMO_indx = 3, min_shift = -1, max_shift = 1 will reduce the active space to the
    # orbitals [2, 3, 4], where orbitals 2,3 are occupied and 4 is unoccupied.
    # So we reduce the initial 6 x 6 matrix to the 3 x 3 matrix
    # This function returns the reduced matrix "M_red".
    #
    # Used in: main.py/main/run_MD/gamess_to_libra


    if(HOMO_indx+min_shift<0):
        print "Error in reduce_matrix: The min_shift/HOMO_index combination result in the out-of-range error for the reduced matrix"
        print "min_shift = ", min_shift
        print "HOMO_index = ", HOMO_index
        print "Exiting...\n"
        sys.exit(0)

    sz = max_shift - min_shift + 1

    if(sz>M.num_of_cols):
        print "Error in reduce_matrix: The size of the cropped matrix is larger than the size of the original matrix"
        print "size of the corpped matrix = ", sz
        print "size of the original matrix = ", M.num_of_cols
        print "Exiting...\n"
        sys.exit(0)

    M_red = MATRIX(sz,sz)
    pop_submatrix(M,M_red,range(HOMO_indx+min_shift,HOMO_indx+max_shift+1))


    return M_red


