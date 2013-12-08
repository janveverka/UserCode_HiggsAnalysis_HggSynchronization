Update on VH hadronic
Presented by Francesco MICHELI on 18 Oct 2013 from 17:00 to 17:20
Session: Higgs to gammagamma Working Meeting 
https://indico.cern.ch/contributionDisplay.py?contribId=44&sessionId=8&confId=274015
Slides micheli_hgg_20131018.pdf
https://indico.cern.ch/getFile.py/access?contribId=44&sessionId=8&resId=0&materialId=slides&confId=274015

VH hadronic selection
Presented by Francesco MICHELI on 16 Oct 2013 from 14:20 to 14:40
Session: Hgg working meeting 
https://indico.cern.ch/contributionDisplay.py?contribId=25&sessionId=16&confId=274015
Slides
micheli_hgg20131015.pdf
VHhad_genComposition.pdf
https://indico.cern.ch/materialDisplay.py?contribId=25&sessionId=16&materialId=slides&confId=274015

Diphoton MVA cuts: Section 17.2, Table 45, Page 183
https://twiki.cern.ch/twiki/pub/CMS/HggAnalyisNote13253/AN-13-253_temp.pdfDielectrons: pick the pair with the highest MVA ID.
Dimuons: pick the two hardes muons.


    bool passPreselection = (mass > 100 &&
                             mass < 180 &&
                             ph1pt > mass/3 &&
                             ph2pt > mass/4 &&
                             ph1id > -0.2 &&
                             pho1id > -0.2);
