#*********************************************************************************
#* Copyright (C) 2016 Ekadashi Pradhan and Alexey V. Akimov
#* 
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 2 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/
######################################################################
#
# Analysis of azobenzene trajectory
#
######################################################################


# Fisrt, we add the location of the library to test to the PYTHON path
#cwd = os.getcwd()
#cwd = "/projects/alexeyak/Software/libracode-code/tests/study2"
#cwd = "/home/Alexey_2/Programming/Project_libra/tests/study2"

#print "Current working directory", cwd

import os
import sys
import math
import copy

if sys.platform=="cygwin":
    from cyglibra_core import *
elif sys.platform=="linux" or sys.platform=="linux2":
    from liblibra_core import *
from libra_py import *




def angle(ri,rj,rk,rl):
    t = VECTOR()
    u = VECTOR()
    rp = VECTOR()

    direction = 1.0  # =1 - torsion;  =-1 - dihedral angle


#    print ri.x, ri.y, ri.z
#    print rj.x, rj.y, rj.z
#    print rk.x, rk.y, rk.z
#    print rl.x, rl.y, rl.z
     
    rij = ri - rj
    rkj = rk - rj
    rlk = rl - rk

#    print rij.x, rij.y, rij.z
#    print rkj.x, rkj.y, rkj.z
#    print rlk.x, rlk.y, rlk.z

    t.cross(rij, rkj)
    t = direction*t  

    u.cross(rlk, rkj)
    modt = t.length()
    modu = u.length()

#    print "t= ",t.x, t.y, t.z
#    print "u= ",u.x, u.y, u.z

    phi = 0.0

    if((modt!=0.0) and (modu!=0.0)):
        cos_phi = (t*u)/(modt*modu)
#        print "cos_phi= ",cos_phi
        if(cos_phi>= 1.0):
            cos_phi=1.0
        elif(cos_phi<=-1.0):
            cos_phi=-1.0

        rp.cross(t,u)
        sgn = 0.0
        if rkj*rp <0.0:
            sgn = -1.0
        else:
            sgn = 1.0

        phi = sgn*math.acos(cos_phi)

    
    return phi



def run(filename):

    #C3 - N12 - N13 - C14
    f = open(filename,"r")
    A = f.readlines()
    f.close()

    sz = len(A)
    nsnaps = sz / (24 + 2)

    print "number of snaps = ", nsnaps

    r1 = VECTOR()
    r2 = VECTOR()
    r3 = VECTOR()
    r4 = VECTOR()

    f1 = open(filename+"_dihedral.txt","w")

    prev = 0.0
    cum = 0.0

    for t in xrange(nsnaps):
        s_C1 = A[t*26+(2+2)].split()
        s_N2 = A[t*26+(11+2)].split()
        s_N3 = A[t*26+(12+2)].split()
        s_C4 = A[t*26+(13+2)].split()

#        print s_C1
#        print s_N2
#        print s_N3
#        print s_C4
 
        r1.x, r1.y, r1.z = float(s_C1[1]), float(s_C1[2]), float(s_C1[3])
        r2.x, r2.y, r2.z = float(s_N2[1]), float(s_N2[2]), float(s_N2[3])
        r3.x, r3.y, r3.z = float(s_N3[1]), float(s_N3[2]), float(s_N3[3])
        r4.x, r4.y, r4.z = float(s_C4[1]), float(s_C4[2]), float(s_C4[3])
    
        ang = angle(r1,r2,r3,r4)
#        print math.degrees(ang)
        d_ang = ang - prev   # change of angle during this step 

        d_ang_corr = d_ang

        if d_ang>math.pi:
            d_ang_corr = d_ang - 2.0*math.pi
        elif d_ang<-math.pi:
            d_ang_corr = d_ang + 2.0*math.pi

        cum = cum + d_ang_corr
        prev = ang
        

        f1.write("%8.5f  %8.5f  %8.5f\n" % ( t, cum, math.degrees(math.fabs(ang)) ) )
    f1.close()
    

run("md_0_1_0.xyz")
#run("tsh_copy_1.xyz")

