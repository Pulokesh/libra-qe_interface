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

