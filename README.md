# Libra-GAMESS_interface

   This file introduces how to execute Libra-GAMESS_interface.

0. Install Libra and GAMESS on your PC or server.
   For installation, access the websites below:
    Libra:  http://www.acsu.buffalo.edu/~alexeyak/libra/index.html
   GAMESS:  http://www.msg.ameslab.gov/gamess/

1. Create a working directory,say, /home/work . 

2. There, create input files(*.inp).(H2O.inp and 23waters.inp in ".../libra-gamess_interface/run" are the simple examples.)
   For more details about how to create that, 
   please see the website http://www.msg.ameslab.gov/gamess/GAMESS_Manual/input.pdf .
   Here, Keep in mind 3 things.
   A. Only semi-empirical methods have been connected to libra so far;
      set GBASIS=MNDO, AM1, PM3, or RM1 in $BASIS section. 
   B. Set RUNTYP=GRADIENT in $CONTROL section.
   C. Use cartesian coordinates in $DATA section like this:

      Cn 1

      C  6.000000 4.377921 -4.769170 -2.758971
      C  6.000000 3.858116 -4.331728 -3.995136
      C  6.000000 2.478331 -4.387937 -4.267327
                           .
                           .
                           .
   
   * set blank line between "Cn 1" and 1st coordinate line.

3. For convinience, copy run_gms.py in ".../libra-gamess_interface/run" to the working place.

4. Modify copied run_gms.py for calculation.
   Concretely, set variables for GAMESS, Molecular Dynamics(MD), excited electron dynamics, and debugs.
   See the input manual in ".../libra-gamess_interface/run" to know more about the variables.

5. copy elements.txt in ".../libra-gamess_interface/run" to the working directory.

6. Create "res" and "sd_ham" directories under the working place, where the results will be output.

7. When the precedures above are finished, it is the time to execute this program.
   Here, 2 types of execution can be used.
   A. Only invoke "python run_gms.py" in the working place.
   B. Use queuing system. submit_templ_gms.lsf or submit_templ_gms.slurm in ".../libra-gamess_interface/run" are the simple examples for using this.
      Modify the files following your queuing system.   
   
8. After the calculation finished, the results will be set in "res" directory.