UserCode_HiggsAnalysis_HggSynchronization
=========================================

Common scripts for the synchronization of the CMS analysis of the Higgs decay to two photons

Comparisons of 16 December
--------------------------
   * The definitions of probmva and pho*_EnScale differ. Which do we pick?
   * Expand the comparisons as proposed by Pasquale.
   * Add the overall yields per fwk and yields per run period per fwk.
   * Add vh_had_massjj (?) variable in MIT.
   * Add variables pho*_sc{Eta,Phi}
   * Fix typos for photon ID MVA input names.
   * Consistent axes for cat: Globe on y and MIT on x.
   * Count number of unique lumis

Comparisons of 18 December
--------------------------
  * Check exclusive events in 7 TeV (two ttH)
  * Check all dijet migrations if they are need boundaries
  * plot phiWidth, idmva and probmva on full scale, plot absolute differences
  * 8 TeV excl cats: one VH MET event only selected by MIT not understood
    * Understand dijet difference
    * Understand phiWidth issue
  * 7 TeV
    * Understand Unique events
    * Understand all the exclusive and dijet events
  * Reconfirm CiC
  * Check location of 7 TeV desync sigmaE events

Slides of 18 December
---------------------
	* Send Josh a number of untagged unique events in both 7 and 8 TeV and desync excl events that have not been understood.
	* plot phiWidth, idmva and probmva on full scale, plot absolute differences
	* 8 TeV excl cats: one VH MET event only selected by MIT not understood
		* Understand dijet difference
		* Understand phiWidth issue
	* 7 TeV
		* Understand Unique events
		* Understand all the exclusive and dijet events

     9 only Globe: vtxprob, pho1_sieip, sigmamom_wrong_vtx, sigmamom, pho2_sieip, ptom1, dphi, ptom2, pho2_s4ratio
    12 only MIT: ele2_pt, pho2_scEta, pho2_cieip, rVtxSigmaMoM, ele2_phi, pho1_scEta, ele2_eta, pho1_cieip, pho1_pfChargedIsoGood03, rho, pho2_s4Ratio, wVtxSigmaMoM

