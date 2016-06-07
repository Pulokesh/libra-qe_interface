#*********************************************************************************
#* Copyright (C) 2016 Ekadashi Pradhan, Alexey V. Akimov
#*
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 2 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/

## \file main.py
# This module sets initial parameters from GAMESS output, creates initial system, 
# and executes runMD script.
# 
# It returns the data from runMD for debugging the code.

import os
import sys
import math
import copy

if sys.platform=="cygwin":
    from cyglibra_core import *
elif sys.platform=="linux" or sys.platform=="linux2":
    from liblibra_core import *
from libra_py import *





from create_input_gms import *
from create_input_qe import *
from x_to_libra_gms import *
from x_to_libra_qe import *
from md import *


def main(params):
    ##
    # Finds the keywords and their patterns and extracts the parameters
    # \param[in] params  the input data from "submit_templ.slm", in the form of dictionary
    # Returned data:
    # test_data - the output data for debugging, in the form of dictionary
    # data - the data extracted from gamess output file, in the form of dictionary
    #
    # This function prepares initial parameters from GAMESS output file
    # and executes classical MD in Libra and Electronic Structure Calculation in GAMESS 
    # iteratively.
    # Parallelly, it executes TD-SE and SH calculation for simulating excited eletronic dynamics.
    #
    # Used in:  run.py

    dt_nucl = params["dt_nucl"]
    nstates = len(params["excitations"])
    ninit = params["nconfig"]  
    SH_type = params["tsh_method"]

    num_SH_traj = 1
    if SH_type >= 1: # calculate no SH probs.  
        num_SH_traj = params["num_SH_traj"]

    ntraj = nstates*ninit*num_SH_traj

    #######
    active_space = [6,7,8]  # Lets use HOMO and LUMO orbitals first
    print "Implement the algorithm to define the active space"
    #sys.exit(0)
    ######

    ################# Step 0: Use the initial file to create a working input file ###############

    if params["interface"]=="GAMESS": 
        os.system("cp %s %s" %(params["gms_inp0"], params["gms_inp"]))

    elif params["interface"]=="QE":
        for ex_st in xrange(nstates):
            os.system("cp x%i.scf.in x%i.scf_wrk.in" % (ex_st, ex_st))


    #### Step 1: Read initial input, run first calculation, and initialize the "global" variables ####

    # Initialize variables for a single trajectory first!
    label, Q, R, ao, tot_ene = [], None, None, [], None
    sd_basis = []
    all_grads = []
    e = MATRIX(nstates,nstates)
    
    if params["interface"]=="GAMESS":

        params["gms_inp_templ"] = read_gms_inp_templ(params["gms_inp"])
        exe_gamess(params)
        label, Q, R, grads, e, c, ao, tot_ene = gms_extract(params["gms_out"],params["debug_gms_unpack"])
        sd_basis.append(c)
        all_grads.append(grads)

    
    elif params["interface"]=="QE":
        params["qe_inp_templ"] = []
        for ex_st in xrange(nstates):

            params["qe_inp_templ"].append( read_qe_inp_templ("x%i.scf_wrk.in" % ex_st) )
            exe_espresso(ex_st)
            flag = 0
            tot_ene, label, R, grads, sd_ex, params["norb"], params["nel"], params["nat"], params["alat"] = qe_extract("x%i.scf.out" % ex_st, flag, active_space, ex_st)

            sd_basis.append(sd_ex)
            all_grads.append(grads)
            e.set(ex_st, ex_st, tot_ene)


    # Now, clone the single-trajectory variables, to initialize the bunch of such parameters
    # for all trajectories
    sd_basis_list = []
    ham_el_list = []    
    ao_list = []
    e_list = []
    grad_list = []
    label_list = []
    Q_list = []
    R_list = []

    for i in xrange(ntraj):
        if params["interface"]=="GAMESS":
            # AO
            ao_tmp = []
            for x in ao:
                ao_tmp.append(AO(x))
            ao_list.append(ao_tmp)
            # Q
            qq  = []
            for i in xrange(len(label)):
                qq.append(Q[i])
            Q_list.append(qq)

        # E 
        e_list.append(MATRIX(e))

        # Slater determinants
        # eventually, the ordering is this: sd_basis_list[traj][ex_st] - type CMATRIX
        sd_basis_tr = []
        for sd in sd_basis:        
            sd_basis_tr.append(CMATRIX(sd))
        sd_basis_list.append(sd_basis_tr)

        # Gradients
        # eventually, the ordering is this: grad_list[traj][ex_st][n_atom] - type VECTOR
        grd2 = []
        for grad in all_grads: # over all excited states
            grd1 = []
            for g in grad:     # over all atoms
                grd1.append(VECTOR(g))
            grd2.append(grd1)
        grad_list.append(grd2)
    

        # Coords
        rr = []
        for r in R:
            rr.append(VECTOR(r))
        R_list.append(rr)

        # Labels
        lab = []
        for i in xrange(len(label)):
            lab.append(label[i])
        label_list.append(lab)
        


    ################## Step 2: Initialize molecular system and run MD part with TD-SE and SH####

    print "Initializing nuclear configuration and electronic variables..."
    rnd = Random() # random number generator object
    syst = []
    el = []

    # all excitations for each nuclear configuration
    for i in xrange(ninit):
        print "init_system..." 
        for i_ex in xrange(nstates):
            for itraj in xrange(num_SH_traj):
                print "Create a copy of a system"  
                df = 0 # debug flag
                # Here we use libra_py module!
                # Utilize the gradients on the ground (0) excited state
                x = init_system.init_system(label_list[i], R_list[i], grad_list[i][0], rnd, params["Temperature"], params["sigma_pos"], df, "elements.txt")
                syst.append(x)    

                print "Create an electronic object"
                el.append(Electronic(nstates,i_ex))
    
    # set list of SH state trajectories

    print "run MD"
    if params["interface"]=="GAMESS":
        run_MD(syst,el,ao_list,e_list,sd_basis_list,params,label_list, Q_list, active_space)
    elif params["interface"]=="QE":
        run_MD(syst,el,ao_list,e_list,sd_basis_list,params,label_list, Q_list, active_space)
    print "MD is done"

