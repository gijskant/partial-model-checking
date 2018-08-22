## PREPARE

export PATH=/Users/vdpol/Gijs/mCRL2.app/Contents/bin:/Users/vdpol/Gijs/PMC/scripts:$PATH

mkdir data
cd data

## PREPROCESSING and LINEARISATION

mcrl22lps -f -lregular2 ../exampleXY.mcrl2 example.lps
mcrl22network.py ../exampleXY.mcrl2

lpspp example.lps  example.pp
lpspp X_1.lps X_1.pp
lpspp Y_1.lps Y_1.pp

## CHECKING THE FORMULA

lps2pbes -f../reach.mcf example.lps example.reach.pbes
pbespp example.reach.pbes example.reach.pp

## Quotienting Y

formulaquotient -v -IPS -nexampleXY.net ../reach.mcf example.reachY.pbes
pbespp example.reachY.pbes example.reachY.pp

## Quotienting X

mcrl22network.py ../exampleYX.mcrl2
formulaquotient -v -IPS -nexampleYX.net ../reach.mcf example.reachX.pbes
pbespp example.reachX.pbes example.reachX.pp
