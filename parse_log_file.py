#!/usr/bin/env python

import os, sys
import shutil
import argparse

import tempfile

import subprocess as sp

import pprint

import platform

import re

from operator import itemgetter
 
def main():

    comm_args = parse_args()

    logfile = comm_args['logfile']
    verbose = comm_args['verbose']
    do_sort = comm_args['sorted']

    with open(logfile) as f:
        content = [line.rstrip() for line in f]

    #print content

    # This will have each line in our file as a separate member of a list
    #loginp = [[i] for i in content]
    #print loginp

    match_F90 = re.compile('.*mpi(fort|f90|f08|ifort).*(___\.f90|\.F90|\.F|\.f)$')
    F90files = filter(match_F90.match,content)
    #print F90files

    rgx_list = [
        # Remove esma_timer
        '^.*esma_timer.sh\s+[\w]*\.o\srun', 

        # Match -I/ directories
        '\s+-I/[\w/.-]*',

        # Match -Iword directories
        '-I[\w/.-]*\s+',

        # Match -I.
        r'-I.',

        # Match -D macros
        '\s+-D[\w/.-=]*', 

        # Remove mpi(fort|ifort|f90)
        'mpi(fort|ifort|f90|f08)\s+',

        # Remove -o file
        '-o\s+[\w/-]*\.o',

        # Remove -c
        r'-c '
        ]

    output = []
    for line in F90files:
        new_line = line
        for rgx in rgx_list:
            new_line = re.sub(rgx,'',new_line)
        new_line = re.sub(' +',' ',new_line)
        new_line_reversed = tuple(reversed(tuple(new_line.rsplit(' ',1))))
        output.append(new_line_reversed)

    if do_sort:
        namesort = itemgetter(0)
        output = sorted(output,key=namesort)

    for item in output:
        try:
            print ("File: {}\n   Options: {}\n").format(*item)
        except IndexError:
            print ("File: {}\n   Options: NONE\n").format(item[0])







def parse_args():

    p = argparse.ArgumentParser(description='''Utility to quickly create experiment. 
            At present, it creates an experiment in the same manner as gcm_setup 
            would with home and experiment directories as usual.''')

    # Verbosity
    # ---------
    p.add_argument('-v','--verbose', help="Verbose output", action='store_true')

    # Quietosity
    # ----------
    #p.add_argument('-q','--quiet', help="Quietly Setup Experiment (no printing)", action='store_true')

    # ------------------
    # Required Arguments
    # ------------------

    p.add_argument('logfile', type=str, help="Log File to Parse")

    # Sort Output
    # -----------
    p.add_argument('--sorted', help="Print sorted output (by filename)", action='store_true')

    ## ------------------
    ## Optional Arguments
    ## ------------------

    ## Experiment Description
    ## ----------------------
    #p.add_argument('--expdsc', help="Experiment Description (Default: same as expid)", type=str)

    #try:
        #with open(os.path.expanduser('~/.EXPDIRroot'),'r') as expdirroot:
            #default_root = expdirroot.read().strip()
    #except IOError:
        #default_root = None

    ## Experiment Directory
    ## --------------------
    #p.add_argument('--expdir', help="Experiment Directory Root *NOT CONTAINING EXPID* (Default is what is in ~/.EXPDIRroot: %s )" % default_root, default=default_root, type=str)

    ## Atmospheric Horizontal Resolution
    ## ---------------------------------
    #horz_choices = ['a','b','c','d','e','c12','c24','c48','c90','c180','c360','c720','c1440','c2880']
    #p.add_argument('--horz', help="Horizontal Resolution (Default: c48 on clusters, c12 on desktop)", type=str, choices=horz_choices)

    ## Atmospheric Vertical Resolution
    ## -------------------------------
    #vert_choices = ['72','132']
    #p.add_argument('--vert', help="Vertical Resolution (Default: 72) ", type=str, choices=vert_choices)

    ## Data Ocean
    ## ----------
    #ocean_choices = ['o1','o2','o3','CS']
    #p.add_argument('--ocean', help="Data Ocean Resolution (Default: o1)", type=str, choices=ocean_choices)

    ## Land Surface Model
    ## ------------------
    #p.add_argument('--land', help="Land Surface Model (Default: 1)", type=str, default='1', choices=['1','2'])

    ## Runoff Model
    ## ------------
    #p.add_argument('--runoff', help="Runoff Routing Model (Default: no)", type=str, default='no',choices=['yes','no'])

    ## Gocart Aerosols
    ## ---------------
    #p.add_argument('--gocart', help="GOCART aerosols: Actual (A) or Climatological (C) (Default: A on clusters, C on desktops)", type=str, default='A', choices=['A','C'])

    ## GOCART emissions
    ## ----------------
    #p.add_argument('--emission', help="GOCART Emissions to use (Default: MERRA2)", type=str, default='MERRA2', 
            #choices=['MERRA2','PIESA','CMIP','NR','MERRA2-DD','OPS'])

    ## History Template to use
    ## -----------------------
    #p.add_argument('--history', help="History Template (Default: Current)", type=str, default='Current')

    ## Account
    ## -------
    #p.add_argument('--account', help="Account Number to Use (Default: g0620 at NCCS, g26141 at NAS)", type=str, default='g0620')

    ## Use GPU
    ## -------
    #p.add_argument('--gpu', help="Setup Experiment to use GPUs", action='store_true')

    return vars(p.parse_args())

if __name__ == "__main__":
    main()


