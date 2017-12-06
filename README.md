# Libra-QuantumEspresso_interface

   Getting started with libra-QE interface
## Required softwares
   Libra and Quantum Espresso
   >Download and install [Libra] and [Quantum Espresso]  <br/>
   >Instructions for Libra installation are provided in Libra website [link1].

## Clone or Download libra-qe_interface
   You can download ZIP file in to your computer or clone entire folder in to your local working directory.
   > Libra-X is located here [Libra-X]
   > For cloning, Copy path to clipboard, then go to your local working directory and type <br/>
   > git clone path-of-libra-qe_interface <br/>

## Working with Libra-QuantumEspresso interface
   Go to libra-qe_interface. In this directory, you will find "src" and "run" folders.
 - src : Where all the source codes are placed. You don't need to change any files in this directory. If new updates are
         available, git pull will automatically update it.
 - run : Contains submission and run scripts. System specific details can be provided in the run_qe.py script. 

### Step-by-Step
1. Copy "run" to a working directory, name it as you like, say "run0". Go to "run0" directory.
2. Create res, sd_ham, and mo_ham directories where results will be saved.
3. Edit run_qe.py script as required. ([How To Edit Run Script](#how-to-edit-run-script))
4. Edit "x_i.scf.in", "x_i.exp.in" files. ([Editing QE Input Files](#editing-qe-input-files))
   These are Quantum espresso input file for SCF and wavefunction export 
   calculations respectively. "_i" extension for each of the electronic
   states included in the NAMD calculation.
5. submit submit_templ_qe.slm submission script. If it is a small calculation, you can run on the head
   node by just "python run_qe.py"
6. Upon completion of caculation, results will be printed in res and sd_ham folders.

  

## How To Edit Run Script
```sh
There are many system specific parameters in thi run_qe.py script
and they are presented as params["name-of-the-parameter"]

 - Create a new use index number. Specify "libra_bin_path" and "libra_qe_int_path" for the user.
 - Description of other simulation parameters such as number of processors, number of snaps, 
   nuclear time step, etc., are provided in the run_qe.py script.
 - One of the most important parameters is params["excitations"] 
   which is constructed by excitation() object. This excitation() objct takes 
   four integer arguments for a specific electronic state. From orbital(fo) from spin(fs) 
   to orbital(to) to spin(ts).
  -- As an example, excitation(0101) presents S0 (ground state), 
     excitation(0111) define S1 excited state. Here, orbital numbering 
     starts from HOMO (0). Alpha (up) spin labeled as 1 and beta 
     (down) spin indexed as -1.
 
   
```

## Editing QE Input Files
```sh
While most of the Quantum Espresso input documentation are available in 
their website, some important requirement for libra-QE are given here.
 - pseudo_dir = 'path of pseudo potential files',
 - prefix = 'xi', i varies for different electronic states, eg., for S0, pseudo_dir = "x0" 
 - nspin = 2, this is for spin polarized calculation
 - K_POINTS automatic, For current version, later multiple k-points could be included.
   1 1 1  0 0 0
   or use
   K_POINTS gamma, This results faster calculation as one half of the wavefunction is optimized
   during SCF calculation. The other half is reconstructed using libra library
 - OCCUPATIONS, This is the most important input specification for Delta-SCF calculation
   Alpha and beta spins orbitals occupations are provided. Single line break is requred between them.
   Although integer occupation number is provided, if SCF does not converge due
   to degeneracy problem or multireference character of the electronic wavefunction, a fermi 
   population is considered and calculation is restarted. This is done automatiocally in the main
   script.
```

----------------------------------------------
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

[Quantum Espresso]: <http://www.msg.ameslab.gov/gamess/>
[Libra]: <http://www.acsu.buffalo.edu/~alexeyak/libra/index.html>
[link1]: <http://www.acsu.buffalo.edu/~alexeyak/libra/installation.html>
[Libra-X]:<https://github.com/Quantum-Dynamics-Hub/Libra-X>
