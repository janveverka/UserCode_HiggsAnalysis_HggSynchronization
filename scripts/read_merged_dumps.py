#!/usr/bin/env python

import ROOT

outfile = ROOT.TFile.Open('merged_dump.root', 'RECREATE')
tree = ROOT.TTree('sync', 'merged synch tree')
branch_descriptor   = 'run/l:lumi:event:bjet_csv[2]/F:cat[2]:cosThetaStar[2]:ele1_eta[2]:ele1_phi[2]:ele1_pt[2]:ele2_eta[2]:ele2_phi[2]:ele2_pt[2]:jet1_eta[2]:jet1_phi[2]:jet1_pt[2]:jet2_eta[2]:jet2_phi[2]:jet2_pt[2]:mass[2]:met[2]:met_phi[2]:mu1_eta[2]:mu1_phi[2]:mu1_pt[2]:mu2_eta[2]:mu2_phi[2]:mu2_pt[2]:numBJets[2]:numJets[2]:pho1_EnScale[2]:pho1_e[2]:pho1_eErr[2]:pho1_eta[2]:pho1_phi[2]:pho1_r9[2]:pho2_EnScale[2]:pho2_e[2]:pho2_eErr[2]:pho2_eta[2]:pho2_phi[2]:pho2_r9[2]:probmva[2]:tth[2]:uncorrMet[2]:uncorrMet_phi[2]:vertexId0[2]:vertexMva0[2]:vhHad[2]:vhHad_mass_dijet[2]:vhLep[2]:vhMet[2]'
tree.ReadFile('test3.txt', branch_descriptor)
#tree.Write()
outfile.Write()
outfile.Close()

