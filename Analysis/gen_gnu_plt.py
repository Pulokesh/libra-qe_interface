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

# This script generates gnuplot script for
# dihedral angle/torsional angle scan for
# all the trajectories


f1 = open("plt_gnu_dhl","w")
f1.write("set terminal pngcairo font \"arial,24\" size 800, 600 enhanced rounded truecolor \n set lmargin at screen 0.20 \n set rmargin at screen 0.95 \n set bmargin at screen 0.15 \n set tmargin at screen 0.95 \n set xlabel \"time, fs\" offset 0.0, 0.5 \n set ylabel \"Torsional angle, rad\" offset 0.5, 0.0 \n set xtics 50.0 \n set ytics 1.0 \n set xrange [0.0:260] \n set yrange [-1:3.5] \n set key spacing 1.0 font \",24\" \n set key top horizontal \n ")
f1.write("set output \"azo_trans_torsion_NVT_0.001_SET4.png\" \n")
#f1.write("set terminal dumb \n something else \n other things \n")
f1.write("plot ")

for i in range(0,100):
    f1.write("\"run%i/res/md_0_1_0.xyz_dihedral.txt\" u 1:2 w l lw 1 lt -1 notitle , " %i )
f1.close()
