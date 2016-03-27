#
def read_qe_inp_templ(inp_filename):
##
# Reading and storing QE input templet
#

    f = open(inp_filename,"r")
    templ = f.readlines()
    f.close()

    N = len(templ)
    for i in range(0,N):
        s = templ[i].split()
        if len(s) > 0 and s[0] == "celldm(1)" and s[1] == "=":
            sa = s[2].split(',')
            cell_dm = float(sa[0])
            break

    N = len(templ)
    for i in range(0,N):
        s = templ[i].split()
        if len(s) > 0 and s[0] == "ATOMIC_POSITIONS":
            ikeep = i
            break

    # Blank space for the atomic positions
    templ[ikeep+1:N] = []
    for i in xrange(ikeep+1):
        print templ[i]
    


    return cell_dm, templ

