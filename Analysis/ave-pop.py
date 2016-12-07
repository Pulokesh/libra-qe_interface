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

######################################################################
#
# Analysis of Ethylene trajectory; Average population vs. Time(fs)
#
######################################################################

import os
import sys
import math




def run():

    dt = 1.0 / 41.34145  # 41.34145 = 1 fs
    
    # Read a first file   
    sz = []
    #for i in xrange(10):
    for i in range(0,100):
        f = open("run%i/res/sh_pop_ex1.txt"%i,"r")
        A = f.readlines()
        f.close()

        sz.append(len(A))  # how many lines
    mn_sz,mx_sz = min(sz),max(sz)
    print "Number of lines = ", mn_sz,sz.index(mn_sz), mx_sz
    print sz
    mx_run = sz.index(mx_sz)

    f = open("run%i/res/sh_pop_ex1.txt"%mx_run,"r")
    A = f.readlines()
    f.close()

    #sys.exit(0)
    T = []
    P = []
    for a in A:
        tmp = a.split()
        T.append( float(tmp[1]) * dt )
        P.append( 0.0 )
    #print T
    #sys.exit(0)    

    for i in range(0,100):

        f = open("run"+str(i)+"/res/sh_pop_ex1.txt","r")
        A = f.readlines()
        f.close()
        la = len(A)
        if la < mx_sz: # If particular trajectory is not completed
            for j in xrange(mx_sz-la):
                #A.append("1.00 1.00 1.00 1.00 Added lines")
                A.append(A[la-1]) # Keep the last population till end

        for n in xrange(mx_sz):
            tmp = A[n].split()
            P[n] = P[n] + (1.0/100.0) * float(tmp[3]) 
            # If the result is not completed for this trajectory, then dont
            # take it to account
           #P[n] = P[n] 


    f1 = open("relax_total.txt","w")
    for n in xrange(mx_sz):
        f1.write("%8.5f  %8.5f\n" % ( T[n], P[n]) )
    f1.close()
    

run()
