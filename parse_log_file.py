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

multiargs = ['-assume', '-check', '-warn','-align','-heap-arrays','-fp-model','-extend_source']

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
            all_opts = splitline[0]
            for arg in multiargs:
                rgx = arg + ' +(\S+)'
                all_opts = re.sub(rgx,arg+"_\\1", all_opts)
            
            splitline[0] = ' '.join( sorted(all_opts.split()) )

            all_opts = splitline[0]
            for arg in multiargs:
                rgx = arg + '_(\S+)'
                all_opts = re.sub(rgx,arg + " \\1", all_opts)
            splitline[0] = all_opts

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
            all_opts = splitline[0]
            for arg in multiargs:
                rgx = arg + ' +(\S+)'
                all_opts = re.sub(rgx,arg+"_\\1", all_opts)
            
            splitline[0] = ' '.join( sorted(all_opts.split()) )

            all_opts = splitline[0]
            for arg in multiargs:
                rgx = arg + '_(\S+)'
                all_opts = re.sub(rgx,arg + " \\1", all_opts)
            splitline[0] = all_opts

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

    return vars(p.parse_args())

if __name__ == "__main__":
    main()


