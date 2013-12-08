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

from sys import argv
import json 
from pprint import pprint 
from math import fabs
import operator
import array

import ROOT
#from FWLite.Tools.double32ioemulator import Double32IOEmulator

# reduce_precision = Double32IOEmulator()
reduce_precision = lambda x: x

# output_file_name = 'plots.root'

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
                if i != "" and ":" in i:
                    j = i.split(":")
                    if j[0] == "run" or j[0] == "lumi" or j[0] == "event" or j[0] == "type":
                        globals()[j[0]] = abs(int(j[1]))
                    else:
                        vars[j[0]] = float(j[1])
                    
            #if run > lastrun :
            #if run > lastrun or run == 200961 or run == 200976 or run == 201191 :
            #if run > lastrun or run == 201191 :
            if run > lastrun :
                continue
            
            if run<minrun:
                minrun=run
            if run>maxrun:
                maxrun=run
                
            if(lst.has_key((run, lumi, event))):
                #print run, lumi, event
                #print "newVars = ", "mgg:", vars["mgg"]
                #print "oldVars = ", "mgg:", lst[(run,lumi,event)]["mgg"]
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

#_______________________________________________________________________________
def bookHisto(name,nbins,xmin,xmax,relative=False):
    ymin = -xmax*0.2
    ymax = xmax*0.2
    nybins = 2*nbins
    den = ""
    if relative:
        ymin = -0.01
        ymax = 0.01
        nybins = 100
        den = "/ %s" % nameA
    h = ROOT.TH2F(name, 
                  ";%s; %s (%s - %s) %s" % (name, name, nameB, nameA, den),
                  nbins, xmin, xmax, nybins, ymin, ymax)
    h.relative = relative
    return h

#_______________________________________________________________________________
def bookCatHisto(name, nbins):
    return ROOT.TH2F(name,
                     '%s;%s;%s' % (name, nameB, nameA),
                     nbins, -0.5, nbins - 0.5,
                     nbins, -0.5, nbins - 0.5)

#_______________________________________________________________________________
def fillHisto(h, varB, varA, relative=False):
    if nameA == 'MIT':
        varB = reduce_precision(varB)
    elif nameB == 'MIT':
        varA = reduce_precision(varA)
    y=(varB-varA)
    if relative and varA != 0.:
        y /= varA
    h.Fill(varB, y)

#_______________________________________________________________________________
histos = {
    "pho1_eta"     : bookHisto("pho1_eta",     1000,   -3.,   3.0,  True),
    "pho1_phi"     : bookHisto("pho1_phi",     1000, -3.15,  3.15,  True),
    "pho1_e"       : bookHisto("pho1_e",       1000,     0,  2000,  True),
    "pho1_eErr"    : bookHisto("pho1_eErr",    1000,     0,   0.5,  True),
    "pho1_idMVA"   : bookHisto("pho1_idMVA",   1000,    -2,     2, False),
    "pho2_eta"     : bookHisto("pho2_eta",     1000,   -3.,   3.0,  True),
    "pho2_phi"     : bookHisto("pho2_phi",     1000, -3.15,  3.15,  True),
    "pho2_e"       : bookHisto("pho2_e",       1000,     0,  2000,  True),
    "pho2_eErr"    : bookHisto("pho2_eErr",    1000,     0,   300,  True),
    "pho2_idMVA"   : bookHisto("pho2_idMVA",   1000,    -2,     2, False),
    "mass"         : bookHisto("mass",         1800,   100,   180,  True),
    "met"          : bookHisto("met",          1000,     0,  2000,  True),
    "met_phi"      : bookHisto("met_phi",      1000,  -6.5,   6.5, False),
    "uncorrMet"    : bookHisto("uncorrMet",    1000,     0,  2000,  True),
    "uncorrMet_phi": bookHisto("uncorrMet_phi",1000,  -6.5,   6.5, False),
    "diphoMVA"     : bookHisto("diphoMVA",     1000,    -2,     2, False),
    "dijetMVA"     : bookHisto("dijetMVA",     1000,    -2,     2, False),
    "combiMVA"     : bookHisto("combiMVA",     1000,    -2,     2, False),
    "cosThetaStar" : bookHisto("cosThetaStar", 1000,    -2,     2, False),
    "jet1_pt"      : bookHisto("jet1_pt",      1000,     0,  2000,  True),
    "jet1_eta"     : bookHisto("jet1_eta",     1000,    -6,     6, False),
    "jet1_phi"     : bookHisto("jet1_phi",     1000,  -6.5,   6.5, False),
    "jet2_pt"      : bookHisto("jet2_pt",      1000,     0,  2000,  True),
    "jet2_eta"     : bookHisto("jet2_eta",     1000,    -6,     6, False),
    "jet2_phi"     : bookHisto("jet2_phi",     1000,  -6.5,   6.5, False),
    "mu1_pt"       : bookHisto("mu1_pt",       1000,     0,  2000,  True),
    "mu1_eta"      : bookHisto("mu1_eta",      1000,    -6,     6, False),
    "mu1_phi"      : bookHisto("mu1_phi",      1000,  -6.5,   6.5, False),
    "mu2_pt"       : bookHisto("mu2_pt",       1000,     0,  2000,  True),
    "mu2_eta"      : bookHisto("mu2_eta",      1000,    -6,     6, False),
    "mu2_phi"      : bookHisto("mu2_phi",      1000,  -6.5,   6.5, False),
    "ele1_pt"      : bookHisto("ele1_pt",      1000,     0,  2000,  True),
    "ele1_eta"     : bookHisto("ele1_eta",     1000,    -6,     6, False),
    "ele1_phi"     : bookHisto("ele1_phi",     1000,  -6.5,   6.5, False),
    "ele2_pt"      : bookHisto("ele2_pt",      1000,     0,  2000,  True),
    "ele2_eta"     : bookHisto("ele2_eta",     1000,    -6,     6, False),
    "ele2_phi"     : bookHisto("ele2_phi",     1000,  -6.5,   6.5, False),
}

catHistos = {
    'cat'   : bookCatHisto('cat', 15),
    'tth' : bookCatHisto('tth', 4),
    'vhLep' : bookCatHisto('vhLep', 4),
    'vhMet' : bookCatHisto('vhMet', 3),
    'vhHad' : bookCatHisto('vhHad', 3),
    'numJets' : bookCatHisto('numJets', 12),
    'numBJets' : bookCatHisto('numBJets', 6),
}

differences = {}
ratios = {}
for name in histos.keys():
    differences[name] = []
    ratios[name] = []

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

for ev in common:

    setA = list1[ev]
    setB = list2[ev]

    if len(setA) == 0 or len(setB) == 0:
        continue

    repeat=""
    for name, hist in histos.iteritems():
        try:
            fillHisto( hist, setB[name], setA[name], hist.relative )
            differences[name].append((setB[name] - setA[name], ev))
            if abs(setA[name]) > 0.:
                ratios[name].append((setB[name] / setA[name], ev))

        except Exception, e:
            print 'Caught exception', e
            pass
    for name, hist in catHistos.iteritems():
        hist.Fill(setB[name], setA[name])

print "\n"
print "Common %d" % len(common)
#print common
print "============================"
print "Only1 %d" % len(only1)
print "============================"
#print only1

#print "============================"
print "Only2 %d" % len(only2)
print "============================"
#print only2

### pprint(events2)

print "\n"
#print "------------------------------------------------------------------"
print "CAT      ", repr("ANY").rjust(5),
for i in range(0,9):
   #print " ", i,
   print repr(i).rjust(5),
print "   "
print "============================================================================"
print "Common   ",
print repr(len(common)).rjust(5),
for i in range(0,9):
   #print " ", Commoncat[i],
   print repr(Commoncat[i]).rjust(5),
print "   "
#print "Common1  ",
print "Common1  ", 
print repr(len(common)).rjust(5),
for i in range(0,9):
   print repr(CommonOnly1cat[i]).rjust(5),
print "   "
#print "Common2  ",
print "Common2  ", 
print repr(len(common)).rjust(5),
for i in range(0,9):
   #print " ", CommonOnly2cat[i],
   print repr(CommonOnly2cat[i]).rjust(5),
print "   "
print "============================================================================"
print "Only1    ",
print repr(len(only1)).rjust(5),
for i in range(0,9):
   #print " ", Only1cat[i],
   print repr(Only1cat[i]).rjust(5),
print "   "
print "Only2    ",
print repr(len(only2)).rjust(5),
for i in range(0,9):
   #print " ", Only2cat[i],
   print repr(Only2cat[i]).rjust(5),
print "   "
print "============================================================================"

syncfrac=0.002

print "\n"
print "Synchronization w/in",syncfrac,"of the value"
print "============================================================================"

names=histos.keys()
names.sort()
for name in names:
    h = histos[name]
    c = ROOT.TCanvas ( name )
    d = None
    c.SetGrid()
    c.SetLogz()
    c.cd()
    if h.IsA().InheritsFrom(ROOT.TH2.Class()):
        #h.Draw("colz")
        #d = ROOT.TCanvas ( "%s_proj" % name )
        #if not "vertex" in name:
            #d.SetLogy()
        prj = h.ProjectionY()
        #prj.DrawNormalized()
        sync = prj.Integral( prj.FindBin(-syncfrac), prj.FindBin(syncfrac ) )
        all = prj.GetEntries()
        if all > 0:
            print "%s synch : %d / %d = %1.4f RMS = %1.4f" % ( name, sync, all, sync/all, prj.GetRMS() )
            if sync/all < 0.98:
                print name,"needs to be synced!!!!!!!!!!!"
        prj.SetLineColor(ROOT.kBlue)
        prj.Draw()
        c.SaveAs( "plots/%s.png" % name )
        ## Save the same as a log plot
        c.SetLogy(True)
        c.Modified()
        c.Update()
        c.SaveAs( "plots/%s_logy.png" % name )
        c.SetLogy(False)

names = catHistos.keys()
names.sort()
for name in names:
    h = catHistos[name]
    h.SetStats(False)
    c = ROOT.TCanvas(name)
    c.SetGrid()
    c.SetLogz()
    c.cd()
    h.Draw('colz')
    h.Draw('text same')
    c.SaveAs('plots/%s.png' % name)

