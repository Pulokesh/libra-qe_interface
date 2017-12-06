#*****************************************************
#* Copyright (C) 2017 Ekadashi Pradhan
#*****************************************************
import os
import sys
import math

import time

path_org = os.getcwd()

def qe_inp_initializei(ni):
    ##
    # This function reads coordinate file (coord_2d)
    # which is a collection of all the 2D grid points
    # and generate new Quantum Espresso input file

    f = open("coord_2d","r")
    A = f.readlines()
    f.close()
    nat = 24
    a11 = []
    ij = ni*(nat+2)
    for j in range(2,nat+2):
        a1 = []
        a = A[ij+j].split()
        for k in xrange(6):
            a1.append(a[k])
        a11.append(a1)
    f0 = open("run0/x.scf.in","r+")
    A0 = f0.readlines()
    f0.close()
    for ia in xrange(len(A0)):
        la = A0[ia].split()
        if len(la)>0 and la[0] == "ATOMIC_POSITIONS" and la[1]=="(alat)":
            coord_start = ia
    f0 = open("run0/x.scf_wrk.in","w")
    ai = 0
    for ia in xrange(len(A0)):
        la = A0[ia].split()
        if ia > coord_start and ia <(coord_start+nat+1):

            la[1],la[2],la[3] = a11[ai][3],a11[ai][4],a11[ai][5]
            A0[ia] = " ".join(str(x) for x in la)+'\n'
            ai = ai+1
        f0.write(A0[ia])
    f0.close()




def extract_en(inp_str,a4,d4):
    ##
    # This function opens QE output file and extract final total energy
    # and append that along with a4 (ecutwfc) and d4 (ecutrho) to a list V
    # which is finally returned for writing to an output file

    fe = open(inp_str+".out","r")
    AE = fe.readlines()
    fe.close()
    v0 =0.0
    conv = 0
    for ia in xrange(len(AE)):
        la=AE[ia].split()
        if len(la) >0 and la[0]=="!" and la[1]=="total" and la[2]=="energy":
            la0 = AE[ia].split()
            v0 = float(la0[4])
            conv1 = 1
        if conv ==0:
            if len(la) >0 and la[0]=="total" and la[1]=="energy" and la[2]=="=":
                la0 = AE[ia].split()
                v0 = float(la0[3])


    V = []
    V.append(a4)
    V.append(d4) #(a4*d4)
    V.append(v0)
    return V 


def check_job_stat():
    ##
    # This function check job status - if job is completed
    # it returns status = 1

    f = open("run0/x.scf_wrk.out","r")
    A = f.readlines()
    f.close()

    status = 0
    for s in A:
        sa = s.split()
        if len(sa)>0 and sa[0]=="convergence" and sa[1]=="has" and sa[3]=="achieved":
            status = 1 # job completed 
        elif len(sa)>0 and sa[0]=="convergence" and sa[1]=="NOT" and sa[2]=="achieved":
            status = 1 # job completed
    return status

def run_jobs():
    os.chdir("run0")
    os.system("sbatch submit_templ_qe.slm")
    os.chdir(path_org)

def delay_jobs(grd1,grd2):
    ##
    # This function create QE input, submit jobs, check job status,
    # and if the job is completed it extract energy and repeat the 
    # the process for the next iteration.

    a0 = int(time.time())
    T = 20 # Delay time 20 secconds
    ni = 1 # ni # of jobs at a time
    N = len(grd1)*len(grd2)
    nj = len(grd2)
    idone = 0*nj # Previously completed scans
    EN = []
    for i in xrange(len(grd1)):
        for j in xrange(len(grd2)):
            ija =idone+ i*nj+j
            qe_inp_initializei(ija)
            run_jobs()
            a=int(time.time())
            status = 0
            while status !=1: # Until previous job is finished
                while (a - a0)/T != 1 : 
                     a=int(time.time())
                status = check_job_stat() # Check if the last job is completed
                a0 = a
            en0 = extract_en("run0/x.scf_wrk",grd1[i],grd2[j])
            EN.append(en0)
            # While the program is in progress, scanned ppotential energies
            # are output to pot_en_tmp file and you can check the progress
            fen_tmp = open("pot_en_tmp","w")
            for ln in xrange(len(EN)):
                fen_tmp.write("%s \n"%EN[ln])
            fen_tmp.close()
            a0 = a
    # Write a final potential energy file where a line brak is given
    # in order to directly plot 3D (splot) using gnuplot
    fen = open("pot_en","w")
    for ln1 in xrange(len(grd1)):
        for ln2 in xrange(len(grd2)):
            fen.write("%s \n"%EN[ln1*nj+ln2])
        fen.write("\n")
    fen.close()
    # Delete all the junk files and folders so that the working directory, run0 will
    # be clean after 2D scan is finished
    os.system("rm run0/*.out* run0/*wfc* run0/*igk* run0/*mix*")
    os.system("rm -rf run0/*.save")

#--------------------------------------------------
# Main program call
#--------------------------------------------------
grid_a4 =  [(110.0+4.0*x/1.0) for x in range(0,15)] # The other half will be done later
grid_d4 =  [(0.0+6.0*x/1.0) for x in range(0,31)]

delay_jobs(grid_a4,grid_d4)

print "Done"
