#*****************************************************
#* Copyright (C) 2017 Ekadashi Pradhan
#*****************************************************

##
# This function extracts second hyperpolarizability tensor components
# from a G09 output file and calculate averagve hyperpolarizability

import os
import math
import sys

def hyper_comp(RA,ia,iaa):
    
    if iaa <4:
        GC = ["xxxx","yyyy","zzzz","xxyy","xxzz","yyzz"]
    else:
        GC = ["xxxx","yyyy","zzzz","yyxx","zzxx","zzyy"]
    for lb in RA:
        LB1 = lb.split()
        if len(LB1) > 0 and LB1[0] ==GC[ia]:
            break
    return LB1[2]

    

def extract_hyper_components(filename1):

    f=open(filename1,"r")
    A=f.readlines()
    f.close()
    GAF = [["Gamma(0;0,0,0):"],["Gamma(-w;w,0,0)", "w=", "1064.1nm:"],["Gamma(-w;w,0,0)", "w=", "532.0nm:"],["Gamma(-w;w,0,0)", "w=", "473.0nm:"],["Gamma(-2w;w,w,0)", "w=", "1064.1nm:"],["Gamma(-2w;w,w,0)", "w=", "532.0nm:"],["Gamma(-2w;w,w,0)", "w=", "473.0nm:"]]


    for gi in xrange(len(GAF)):
        count = 1
        for i in xrange(len(A)):
            LA = A[i].split()
            if len(LA)>0 and LA[0] == "Second" and LA[2]=="hyperpolarizability,":
                count = count +1

            if len(LA) > 0 and len(GAF[gi])==1 and LA[0] ==GAF[gi][0]:
                if count >1:
                    GA = []
                    for ia in xrange(6): # Components are explicitly specified in the hyper_comp module
                        GA.append(hyper_comp(A[i:len(A)],ia,gi))
            

            elif len(LA) > 0 and LA[0] ==GAF[gi][0] and LA[2]==GAF[gi][2]: 
                if count >1:
                    GA = []
                    for ia in xrange(6): # 
                        GA.append(hyper_comp(A[i:len(A)],ia,gi))

        ##
        # This following block converts 000D+00 format to 000e+00 format
        for i in xrange(len(GA)):
            c0 = GA[i].split("D")
            c0 = c0[0]+"e"+c0[1]
            GA[i] = float(c0)
    
        print "Average_GA for ",GAF[gi]," = ",0.2*(GA[0]+GA[1]+GA[2]+2.0*(GA[3]+GA[4]+GA[5]))
           #Second dipole hyperpolarizability, Gamma (dipole orientation).
         



#-----------------------------------
#  main function calling
#-----------------------------------
extract_hyper_components("test_gamma_hyper.inp")

