# partial-model-checking

Repository with scripts and instructions for a partial model checking technique for networks of LPSs.

```bash
git clone https://github.com/gijskant/mCRL2.git
cmake . -DMCRL2_ENABLE_GUI_TOOLS=OFF -DMCRL2_ENABLE_EXPERIMENTAL=ON -DCMAKE_INSTALL_PREFIX=${prefix}
make && make install
```
You may need to execute `ldconfig` as `root` or run:
```bash
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${prefix}/lib/mcrl2/
```
Install this `mcrl2` variant globally for the Python scripts to work. (This should be adapted in the future.)


## Usage
To convert an mCRL2 model `example.mcrl2` to a network of LPSs:
```bash
./scripts/mcrl22network.py example.mcrl2
```

To perform partial model checking:
```bash
# Compute quotient formula:
formulaquotient -n ${network.net} -o ${output-network.net} ${formula.mcf} ${output-formula.pbes}
```

## Script for creating a network file
```bash
# creates a network <model>.net
./scripts/mcrl22network.py ${model.mcrl2}
```
The scripts call the tool `memtime` for time measurement. See below for instructions on how to get it. N.B.: `mcrl22network` requires the `mcrl2` specification to be in a specific form:

1. All sections (`proc`, `act`, `etc`) need to start on a new line
2. The `init` section is of the form `hide({...}, allow({...}, comm({...}, P1(...) || P2(...) || ... )))`. The commands can be left out, but need to be in this order. No actions or aliases are allowed in the process specification.
3. Processes can have references to other processes, but for the correct interpretation of which actions can occur,
   the script needs the referenced processes to be declared before the referring process.

## Network format
A network can be specified in a text file with the following format:
```
length
<number of LPSs n>
lps_filenames
<lps filename 1>
...
<lps filename n>
synchronization_vector
<n>
{
  (<label_1>, ..., <label_n>, <label>: <label_type>)
  ...
  (<label_1>, ..., <label_n>, <label>: <label_type>)
}
```
Example: Two components (`lps1.lps`, `lps2.lps`). 
The synchronisation vector consists of two elements: `a` and `b` synchronise, 
resulting in action `c`. The same for actions `d` and `e`. 
Note that the order does matter: the first component needs to perform action `a` or `d` 
for the synchronisation to work in the respective cases.
Network `example.net`:
```
length
2
lps_filenames
lps1.lps
lps2.lps
synchronization_vector
2
{
  (a, b, c: Nat)
  (d, e, c: Nat)
}
```
Formula `formula.mcl`:
```
nu X. exists j: Nat . <c(j)>X
```
Executing the tool:
```
> formulaquotient --network=example.net -o q_example.net formula.mcl q_formula.mcl
> cat q_formula.mcl
nu X(n: Nat = 1). exists j: Nat. val(n == j) && <c1(n)>X(n)
> cat q_example.net
length
1
lps_filenames
lps2.lps
synchronization_vector
1
{
  (b, c1: Nat)
  (e, c2: Nat)
}
```
Iteratively:
```bash
formulaquotient -v -I --network=example.net formula.mcl output.pbes
pbessolve -v output.pbes
```
Repeatedly applies quotienting until a PBES remains. 

## Options:
Option | Description
--- | ---
`-v` | Increase verbosity.
`-S` | Simplify formulas.
`-P` | Apply unused parameter elimination.
`-U` | Unfold unguarded recursion.
`-M` | Use a map to store the synchronization vector (should be default).
`-F` | Write intermediate formulas to disk.
`-N` | Write intermediate networks to disk.
`-A` | Attempt to solve an under-approximation of intermediate formulas.

Preferred combination of options:
```bash
formulaquotient -v -MISP -FNA --network=example.net formula.mcl output.pbes
pbessolve -v output.pbes
```

## Other related tools:
```bash
# rewrites quantifiers using the one-point rule and simplifies the formula
formularewr -n ${network.net} ${formula.mcf} ${output-formula.mcf}

# removes unused parameters from the formula
formulaparelm -n ${network.net} ${formula.mcf} ${output-formula.mcf}

# generates an LTS from the network
network2lts ${network.net} -oaut ${lts.aut}
network2lts ${network.net} -odot ${lts.dot}
```
### memtime
We use memtime for measuring time and memory usage:
```bash
git clone http://fmt.cs.utwente.nl/tools/scm/memtime.git
cd memtime
git submodule update --init
./memtimereconf
./configure --prefix=${prefix}
make && make install
```
