#*********************************************************************************
#* Copyright (C) 2016 Ekadashi Pradhan
#* 
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 2 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/



## This code initialize random trajectories
#

import sys
import os
import math


def random_initialize():

    f = open("md_0_0_0.xyz","r")
    #f = open("run%i/res/md_0_0_0.xyz"%i,"r")
    A = f.readlines()
    f.close()

    nat = 24
    for i in range(0,100):
        a11 = []
        #f = open("run10_1/res/md_%i_0_0.xyz"%i,"r")
        #f = open("run10_1/test%i.xyz"%i,"r")
        #f = open("run%i/res/md_0_0_0.xyz"%i,"r")
        #A = f.readlines()
        #print "# of atoms=",float(A[0])
        #f.close()
        ij = i*(nat+2)
        for j in range(2,nat+2):
            a1 = []
            a = A[ij+j].split()
            for k in xrange(4):
                a1.append(a[k])
            a11.append(a1)
        #print a11
        f0 = open("run%i/x0.scf.in"%i,"r+")
        A0 = f0.readlines()
        f0.close()
        for ia in xrange(len(A0)):
            #ln = len(A0[ia].split())
            la = A0[ia].split()
            if len(la)>0 and la[0] == "ATOMIC_POSITIONS" and la[1]=="(alat)":
                coord_start = ia
        f0 = open("run%i/x0.scf.in"%i,"w")
        ai = 0
        for ia in xrange(len(A0)):
            la = A0[ia].split()
            #ai = 0
            if ia > coord_start and ia <(coord_start+nat+1):
                
                la[1],la[2],la[3] = a11[ai][1],a11[ai][2],a11[ai][3]
                A0[ia] = " ".join(str(x) for x in la)+'\n'
                ai = ai+1
            f0.write(A0[ia])
        f0.close()
    
#def random_initialize1():

#    nat = 6
#---------------------------------------------
#	Initialize x1.scf.in files for 100 different trajectories
#---------------------------------------------


    for i in range(0,100):
        a11 = []
        #f = open("run10_1/res/md_%i_0_0.xyz"%i,"r")
        #f = open("run10_1/test%i.xyz"%i,"r")
        #f = open("run%i/res/md_0_0_0.xyz"%i,"r")
        #A = f.readlines()
        #print "# of atoms=",float(A[0])
        #f.close()
        ij = i*(nat+2)
        for j in range(2,nat+2):
            a1 = []
            a = A[ij+j].split()
            for k in xrange(4):
                a1.append(a[k])
            a11.append(a1)
        #print a11
        f0 = open("run%i/x1.scf.in"%i,"r+")
        A0 = f0.readlines()
        f0.close()
        for ia in xrange(len(A0)):
            #ln = len(A0[ia].split())
            la = A0[ia].split()
            if len(la)>0 and la[0] == "ATOMIC_POSITIONS" and la[1]=="(alat)":
                coord_start = ia
        f0 = open("run%i/x1.scf.in"%i,"w")
        ai = 0
        for ia in xrange(len(A0)):
            la = A0[ia].split()
            #ai = 0
            if ia > coord_start and ia <(coord_start+nat+1):

                la[1],la[2],la[3] = a11[ai][1],a11[ai][2],a11[ai][3]
                A0[ia] = " ".join(str(x) for x in la)+'\n'
                ai = ai+1
            f0.write(A0[ia])
        f0.close()


random_initialize()
#random_initialize1()

