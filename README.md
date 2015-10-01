# partial-model-checking
Repository with scripts and instructions for a partial model checking technique for networks of LPSs.
Old instructions are available on http://wwwhome.ewi.utwente.nl/~kant/quotienting_tool/.

```
git clone https://github.com/gijskant/mcrl2-pmc.git
cmake . -DMCRL2_ENABLE_GUI_TOOLS=OFF -DMCRL2_ENABLE_EXPERIMENTAL=ON -DCMAKE_INSTALL_PREFIX=$prefix
make && make install
```
Install this `mcrl2` variant globally for the Python scripts to work. This should be adapted.

To convert an mCRL2 model `example.mcrl2` to a network of LPSs:
```
./scripts/mcrl22network.py example.mcrl2
```

To perform partial model checking:
```
formulaquotient -n<network> -o <output-network> <formula> <output-formula>
```
