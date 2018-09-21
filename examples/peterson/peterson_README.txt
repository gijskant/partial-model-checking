export PATH=/Users/vdpol/Gijs/mCRL2.app/Contents/bin:/Users/vdpol/Gijs/PMC/scripts:$PATH

mcrl22lps petersonN.mcrl2 p.lps
lpssim p.lps
lps2lts -v p.lps

lps2pbes -f alternate.mcf p.lps ap.pbes
pbespgsolve ap.pbes 

lps2pbes -f mutual.mcf p.lps mp.pbes
pbespgsolve mp.pbes 

lps2pbes -f eventual.mcf p.lps ep.pbes
pbespgsolve ep.pbes 

lps2pbes -f eerlijk.mcf p.lps fp.pbes
pbespgsolve fp.pbes 
