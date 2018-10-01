export PATH=/Users/vdpol/Gijs/mCRL2.app/Contents/bin:/Users/vdpol/Gijs/PMC/scripts:$PATH

cd data
mcrl22lps ../petersonN.mcrl2 p.lps
lpssim p.lps
lps2lts -v p.lps

# ENTER(1) and LEAVE(1) actions alternate.
# true
lps2pbes -f ../alternate.mcf p.lps ap.pbes && \
pbespgsolve -v -srecursive ap.pbes

# Mutual exclusion between processes 1 and 2.
# true
lps2pbes -f ../mutual.mcf p.lps mp.pbes && \
  pbespgsolve -v -srecursive  mp.pbes

# When process 1 tries to enter, always eventually process 1 will enter.
# false
lps2pbes -f ../eventual.mcf p.lps ep.pbes && \
  pbespgsolve -v -srecursive ep.pbes

# When 1 and 2 both try to enter, there is an infinite path where
# 1 infinitely often enters, but 2 never enters.
# true
lps2pbes -f ../eerlijk.mcf p.lps fp.pbes && \
  pbespgsolve -v -srecursive fp.pbes
