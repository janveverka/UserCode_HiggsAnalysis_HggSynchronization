#!/usr/bin/env python

# ############################################################################
#
# The script is developed for purposes of synchronizing H->gammagamma analysis
# performed in different frameworks. It takes as input two txt files
# containing event information in format <field_name>:<field_value>, 
# and outputs the following information: 
#
# 1) event counts and printouts of common and unique events
# 2) same as 1) per event category
# 3) level of synchrnoization per <field_name>
# 4) plots of differences per <field_name>
# 
#
# Original version: P.Musella
# Improved version: V.Rekovic  Jan/2013 
# (added synchronization per category)
#
#
# #############################################################################

import sys
from sys import argv
import json 
from pprint import pprint 
from math import fabs
import operator
import array

import ROOT

minrun=99999
maxrun=0

Commoncat = [0] * 10
CommonOnly1cat = [0] * 10
CommonOnly2cat = [0] * 10
Only1cat = [0] * 10
Only2cat = [0] * 10

lastrun=9999999999999

fn1 = argv.pop(1)
fn2 = argv.pop(1)

#_______________________________________________________________________________
def get_sample_name(file_name):
    if 'globe' in file_name.lower():
        return 'Globe'
    elif 'mit' in file_name.lower():
        return 'MIT'
    else:
        return 'ggA'

nameA = get_sample_name(fn1)
nameB = get_sample_name(fn2)

#_______________________________________________________________________________
def getlist(input):
    lst = {}
    lstDuplEvents = {}
    lstRuns = {}

    global minrun, maxrun

    for line in input.split("\n"):
        vars = {}
        try:
            for i in line.replace(": ",":").replace("="," ").replace("\t"," ").split(" "):
                if i != "":
                    j = i.split(":")
                    if j[0] == "run" or j[0] == "lumi" or j[0] == "event" or j[0] == "type":
                        globals()[j[0]] = abs(int(j[1]))
                    else:
                         vars[j[0]] = float(j[1])
                    
            if run > lastrun :
                continue
            
            if run<minrun:
                minrun=run
            if run>maxrun:
                maxrun=run
                
            if(lst.has_key((run, lumi, event))):
                lstDuplEvents[ (run, lumi, event) ] = vars
                continue

            lst[  (run, lumi, event) ] = vars
            lstRuns[  (run) ] = vars
            
        except Exception, e:
            #print line
            print e
            
    evts = lst.keys()
    duplEvts = lstDuplEvents.keys()
    runs = lstRuns.keys()

    print " Number of unique evts    : %d" % ( len(evts) )
    print " Number of duplicated evts: %d" % ( len(duplEvts)-1 )
    print " Number of unique runs: %d" % ( len(runs) )
    return lst


ROOT.gROOT.SetStyle("Plain")
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetOptStat(111111)

file1 = open(fn1)
file2 = open(fn2)

print "\n"
print "list1: %s" % fn1
print "=========================="
list1 = getlist( file1.read() )
print "\n"
print "list2: %s" % fn2
print "=========================="
list2 = getlist( file2.read() )
print "\n"

events1 = list1.keys()
events2 = list2.keys()

common = set(events1).intersection(  set(events2) )
common = list(common)
common.sort()

only1 = list(set(events1) -  set(events2))
only2 = list(set(events2) -  set(events1))

only1.sort()
only2.sort()

nruns = (maxrun - minrun) / 100

first_event = common[0]
varsA = list1[first_event].keys()
varsB = list2[first_event].keys()
varsA.sort()
varsB.sort()
print varsA
print varsB
vars_common = set(varsA).intersection(set(varsB))
vars_common = list(vars_common)
vars_common.sort()
vars_onlyA = list(set(varsA) - set(varsB))
vars_onlyB = list(set(varsB) - set(varsA))
print 'Common vars:', len(vars_common)
print '    %d only %s:' % (len(vars_onlyA), nameA), ', '.join(vars_onlyA) 
print '    %d only %s:' % (len(vars_onlyB), nameB), ', '.join(vars_onlyB) 

print "Writing merged ASCII dump in `merged_ascii_dump.txt'"

leaf_descriptor = 'run/l:lumi:event:%s[2]/F:' % vars_common[0] 
leaf_descriptor += ':'.join([name + '[2]' for name in vars_common[1:]])

with open('merged_ascii_dump.txt', 'w') as ascii_output:
    ascii_output.write('# Merged synch dumps\n')
    ascii_output.write('#     Index 0: %s\n' % fn1)
    ascii_output.write('#     Index 1: %s\n' % fn2)
    ascii_output.write('# Leaf descriptor: ' + leaf_descriptor ) 
    ascii_output.write('\n')
    for ev in common:
        setA = list1[ev]
        setB = list2[ev]
        if len(setA) == 0 or len(setB) == 0:
            continue
        line_items = ['%8d' % i for i in list(ev)]
        for name in vars_common:
            try:
                line_items.append('%10g' % setA[name])
            except KeyError:
                line_items.append('%10g' % -999)
            try:
                line_items.append('%10g' % setB[name])
            except KeyError:
                line_items.append('%10g' % -999)                    
        ascii_output.write('\t'.join(line_items) + '\n')

print "\n"
print "============================"
print "Common %d" % len(common)
print "Only1 %d" % len(only1)
print "Only2 %d" % len(only2)
print "============================"

outname = 'merged.%s.%s.root' % (fn1.replace('.txt', ''), 
                                 fn2.replace('.txt', ''))
outfile = ROOT.TFile.Open(outname, 'RECREATE')
tree = ROOT.TTree('sync', 'merged sync tree')
tree.ReadFile('merged_ascii_dump.txt', leaf_descriptor)
outfile.Write()
outfile.Close()

