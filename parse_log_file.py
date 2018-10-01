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

def cmake_parse(content,sortfiles=None,sortopts=None,macros=None,fullpath=None):

    match_F90 = re.compile('^cd.*(gfortran|ifort|nagfor|pgfortran).*(\.f90|\.F90|\.F|\.f)\.o$')
    F90files = filter(match_F90.match,content)
    #print F90files

    rgx_list = [
        # Peel off the cd and compiler
        '^cd.*(gfortran-[0-9]|gfortran|ifort|nagfor|pgfortran)\s',

        # Match -I/ directories
        '\s+-I/[\w/.-]*',

        # Match -Iword directories
        '-I[\w/.-]*\s+',

        # Match -I.
        r'-I.', 

        # Match -Iword directories
        '-J[\w/.-]*\s+',

        # Remove -c
        r'-c ', 

        # Remove -o
        r'-o\s+CMakeFiles.*$'
        ]

    if not macros:
        rgx_list.append('-D[\w/.-=]*\s+')

    output = []
    for line in F90files:
        new_line = line
        for rgx in rgx_list:
            new_line = re.sub(rgx,'',new_line)
        new_line = re.sub(' +',' ',new_line)
        new_line = new_line.rstrip()

        splitline = new_line.rsplit(' ',1)

        if not fullpath:
            foundfile = splitline[-1]
            splitline[-1] = os.path.basename(foundfile)

        if sortopts:
            splitline[0] = ' '.join( sorted(splitline[0].split()) )

        new_line_reversed = tuple(reversed(tuple(splitline)))
        output.append(new_line_reversed)

    if sortfiles:
        namesort = itemgetter(0)
        output = sorted(output,key=namesort)

    return output

def gmake_parse(content,sortfiles=None,sortopts=None,macros=None):

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
        #'\s+-D[\w/.-=]*', 

        # Remove mpi(fort|ifort|f90)
        'mpi(fort|ifort|f90|f08)\s+',

        # Remove -o file
        '-o\s+[\w/-]*\.o',

        # Remove -c
        r'-c '
        ]

    if not macros:
        rgx_list.append('-D[\w/.-=]*\s+')

    output = []
    for line in F90files:
        new_line = line
        for rgx in rgx_list:
            new_line = re.sub(rgx,'',new_line)
        new_line = re.sub(' +',' ',new_line)
        new_line = new_line.rstrip()

        splitline = new_line.rsplit(' ',1)

        if sortopts:
            splitline[0] = ' '.join( sorted(splitline[0].split()) )

        new_line_reversed = tuple(reversed(tuple(splitline)))
        output.append(new_line_reversed)

    if sortfiles:
        namesort = itemgetter(0)
        output = sorted(output,key=namesort)


    return output
 
def main():

    comm_args = parse_args()

    logfile  = comm_args['logfile']
    verbose  = comm_args['verbose']
    sortfiles  = comm_args['sortfiles']
    sortopts  = comm_args['sortopts']
    macros   = comm_args['macros']
    gmake    = comm_args['gmake']
    cmake    = comm_args['cmake']
    #ninja    = comm_args['ninja']
    fullpath = comm_args['fullpath']

    with open(logfile) as f:
        content = [line.rstrip() for line in f]

    if cmake:
        output = cmake_parse(content,sortfiles,sortopts,macros,fullpath)
    #elif ninja:
        #output = ninja_parse(content,sortfiles,sortopts,macros)
    else:
        output = gmake_parse(content,sortfiles,sortopts,macros)

    #print content

    # This will have each line in our file as a separate member of a list
    #loginp = [[i] for i in content]
    #print loginp

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
    p.add_argument('--sortfiles', help="Print sorted output (by filename)", action='store_true')
    p.add_argument('--sortopts', help="Sort options", action='store_true')

    # Sort Output
    # -----------
    p.add_argument('--macros', help="Include -D macros", action='store_true')

    # GNU Make Log
    # ------------
    p.add_argument('--gmake', help="GNU Make Log",   action='store_true')

    # cmake Make Log
    # --------------
    p.add_argument('--cmake', help="Cmake Make Log", action='store_true')

    # ninja Make Log
    # --------------
    #p.add_argument('--ninja', help="Ninja Make Log", action='store_true')

    # cmake Make Log
    # --------------
    p.add_argument('--fullpath', help="Output full paths (cmake only)", action='store_true')

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


