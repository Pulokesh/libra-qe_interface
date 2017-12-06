#*********************************************************************************
#* Copyright (C) 2017 Ekadashi Pradhan
#* 
#* This file is distributed under the terms of the GNU General Public License
#* as published by the Free Software Foundation, either version 2 of
#* the License, or (at your option) any later version.
#* See the file LICENSE in the root directory of this distribution
#* or <http://www.gnu.org/licenses/>.
#*
#*********************************************************************************/


import os
import sys
import math


path_org = os.getcwd()


#for i in xrange(100):
###################################
#      Creating folders
###################################
#for i in range(1,100):
#    os.system("cp -r run0 run%i"%i)
###################################

###################################
#       Submiting jobs
###################################
#for i in xrange(5):
for i in range(0,100):
    os.chdir("run%i"%i)
    os.system("rm *wfc* *igk* *mix* *.out*")
    os.system("rm -rf x0.save x1.save x0.export x1.export")
    
    os.chdir(path_org)
###################################
    #os.system("rm -rf run%i"%i)
#os.system("cp x0.exp.in wd")
#os.system("cp x1.exp.in wd")
#os.chdir("wd")
print "Done"

