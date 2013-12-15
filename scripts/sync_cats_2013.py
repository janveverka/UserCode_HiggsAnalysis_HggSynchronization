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
import shutil
import os

import ROOT
#from FWLite.Tools.double32ioemulator import Double32IOEmulator

# reduce_precision = Double32IOEmulator()
reduce_precision = lambda x: x

if not os.path.exists('./plots'):
    os.mkdir('./plots')
shutil.copy('./index.php', './plots')

# output_file_name = 'plots.root'
is8tev = True
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

if ('7tev' in fn1.lower() or '7tev' in fn2.lower() or
    'r11ab' in fn1.lower() or '11ab' in fn2.lower()):
    is8tev = False

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
def bookCatHisto(name, nbins, labels=[]):
    hist = ROOT.TH2F(name,
                     '%s;%s;%s' % (name, nameB, nameA),
                     nbins + 1, -1.5, nbins - 0.5,
                     nbins + 1, -1.5, nbins - 0.5)
    for ibin, label in enumerate(labels):
        for axis in [hist.GetXaxis(), hist.GetYaxis()][1:]:
            axis.SetBinLabel(ibin + 1, label)
    return hist

#_______________________________________________________________________________
def fillHisto(h, varB, varA, relative=False):
    if nameA == 'MIT':
        varB = reduce_precision(varB)
    elif nameB == 'MIT':
        varA = reduce_precision(varA)
    y=(varB-varA)
    if relative and varA != 0.:
        y /= varA
    if abs(varA + 999) > 1e-3 and abs(varB + 999) > 1e-3:
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
    "bjet_csv"     : bookHisto("bjet_csv"    , 1000,    -2,     2, False),
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

if is8tev:
    cat_labels = (['MIA'] + 
                  ['Incl %d'  % i for i in range(5)] +
                  ['Dijet %d' % i for i in range(3)] +
                  ['VH Lep 0', 'VH Lep 1', 'VH MET', 'ttH Lep', 'ttH Had',
                   'VH Had', ''])
else:
    cat_labels = (['MIA'] + 
                  ['Incl %d'  % i for i in range(4)] +
                  ['Dijet %d' % i for i in range(2)] +
                  ['VH Lep 0', 'VH Lep 1', 'VH MET', 'ttH', 'VH Had', 
                   ''])

catHistos = {
    'cat'   : bookCatHisto('cat', len(cat_labels) - 1, cat_labels),
    'tth' : bookCatHisto('tth', 4, ['MIA', 'Untagged', 'Hadronic', 
                                    'Leptonic', '']),
    'vhLep' : bookCatHisto('vhLep', 4, ['MIA', 'Untagged', 'Loose', 'Tight',
                                        '']),
    'vhMet' : bookCatHisto('vhMet', 3, ['MIA', 'Untagged', 'Tagged', '']),
    'vhHad' : bookCatHisto('vhHad', 3, ['MIA', 'Untagged', 'Tagged', '']),
    'numJets' : bookCatHisto('numJets', 12, ['MIA'] + ['%d' % i for i in range(12)]),
    'numBJets' : bookCatHisto('numBJets', 6, ['MIA'] + ['%d' % i for i in range(6)]),
}
hist_cat_msync = bookCatHisto('cat_msync', len(cat_labels) - 1, cat_labels)

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

mia_row = {}
for x in vars_common:
    mia_row[x] = -999.
    if x in catHistos:
        mia_row[x] = -1.

for ev in only1:
    list2[ev] = mia_row
for ev in only2:
    list1[ev] = mia_row

for ev in common + only1 + only2:

    setA = list1[ev]
    setB = list2[ev]

    if len(setA) == 0 or len(setB) == 0:
        continue

    repeat=""
    for name, hist in histos.iteritems():
        try:
            fillHisto( hist, setB[name], setA[name], hist.relative )

        except Exception, e:
            print 'Caught exception', e
            pass
    for name, hist in catHistos.iteritems():
        hist.Fill(setB[name], setA[name])
    if 2 * abs(setA['mass'] - setB['mass']) / (setA['mass'] + setB['mass']) < 0.003:
        hist_cat_msync.Fill(setB['cat'], setA['cat'])

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
    if name == 'cat':
        c = ROOT.TCanvas ( name, name, 1000, 700 )
    else:
        c = ROOT.TCanvas(name)
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


## Sum yields over all categories
## Initialize yields
total = {}
msync  = {}; mdesync = {}
onlya  = {}; onlyb   = {}
uniqa  = {}; uniqb   = {}
for label in cat_labels + ['All']:
    msync[label] = mdesync[label] = 0
    onlya[label] = onlyb  [label] = 0
    uniqa[label] = uniqb  [label] = 0

cat_hist = catHistos['cat']
num_cats = cat_hist.GetXaxis().GetNbins() - 2
## This may be confusing: name A and B correspond to the y and x axes, 
## respectively! So the (name, axis) pairs are (A, y), (B, x)
for xbin, xlabel in enumerate(cat_labels):
    xbin += 1
    for ybin, ylabel in enumerate(cat_labels):
        ybin += 1
        bin = cat_hist.GetBin(xbin, ybin)
        content = int(cat_hist.GetBinContent(bin))
        content_msync = int(hist_cat_msync.GetBinContent(bin))
        if xbin == ybin:
            msync['All' ] += content_msync
            msync[xlabel] += content_msync
            mdesync['All' ] += (content - content_msync)
            mdesync[xlabel] += (content - content_msync)
        elif xbin == 1:
            uniqa['All' ] += content
            uniqa[ylabel] += content
        elif ybin == 1:
            uniqb['All' ] += content
            uniqb[xlabel] += content
        else:
            onlya['All']  += content
            onlyb['All']  += content
            onlya[ylabel] += content
            onlyb[xlabel] += content

for c in cat_labels + ['All']:
    total[c] = (msync[c] + mdesync[c] + onlya[c] + onlyb[c] + uniqa[c] + 
                uniqb[c])
total['All'] -= onlya['All']

cat_table = [['ID', 'Category', 'M-Sync', 'M-Desync', 
              'Only '   + nameA, 'Only '   + nameB, 
              'Unique ' + nameA, 'Unique ' + nameB],]
for cat_id, label in [(-1, 'All'),] + list(enumerate(cat_labels)):
    row = ['%2d' % (cat_id - 1), label]
    for events in [msync, mdesync, onlya, onlyb, uniqa, uniqb]:
        row.append(str(events[label]))
    cat_table.append(row)

## Viva obfuscation! These are widths of the table columns
widths = map(lambda column: max(map(len, column)), zip(*cat_table))

header = cat_table[0]
del cat_table[0]
header = [item.ljust(width) for item, width in zip(header, widths)]
col_sep = '   '

report = []
report.append('*** EVENTS ***')
report.append(col_sep.join(header))
report.append('-' * (sum(widths) + len(col_sep) * (len(widths) - 1)))
## More Python obfusly
justifily = [str.rjust, str.ljust] + (len(widths) - 2) * [str.rjust]
for row in cat_table:
    if row[1] in ['MIA', '']:
        continue
    row = [just(i, w) for just, i, w in zip(justifily, row, widths)]
    report.append(col_sep.join(row))
report.append('')
report.append('*** PERCENTAGES ***')
report.append(col_sep.join(header))
report.append('-' * (sum(widths) + len(col_sep) * (len(widths) - 1)))
for row in cat_table:
    label = row[1]
    if label in ['MIA', '']:
        continue
    prow = row[:2]
    for i in row[2:]:
        if total[label] > 0:
            prow.append('%.2f' % (100 * float(i) / total[label]))
        else:
            append('-')
    prow = [just(i, w) for just, i, w in zip(justifily, prow, widths)]
    report.append(col_sep.join(prow))


report_file_name = './plots/summary.txt'
with open(report_file_name, 'w') as report_file:
    report_file.write('\n'.join(report))

