# Example: Peterson's mutual exclusion algorithm

We have several version of Peterson's algorithm:

1. The version for two parties, taken from Jeroen Keiren's 
[parity game benchmarks repository](https://github.com/jkeiren/paritygame-generator),
from the collection of model checking problems, with a few modifications.

2. The version for _N_ parties in two variants, based on the 
   [description on Wikipedia](https://en.wikipedia.org/wiki/Peterson's_algorithm):
    - [petersonN.mcrl2](petersonN.mcrl2), a generic specification instantiated for 3 parties;
    - the `peterson.N.mcrl2` files, generated using the [petersonN.py](petersonN.py) script.

This algorithm is described in detail in [Herlihy & Shavit (2008): The Art of Multiprocessor Programming] and
[Raynal (2013): Concurrent Programming: Algorithms, Principles, and Foundations].

## Version for _N_ parties

### Generate a specification

```bash
./petersonN.py <N> > peterson.<N>.mcrl2
```

### Prepare a network of Linear Process Equations (LPEs)

```bash
mkdir data
pushd data
../../../scripts/mcrl22network.py ../peterson.5.mcrl2
```

### Run the quotienting tool

```bash
# Quotienting without approximation on intermediate formulae
formulaquotient -v -IPS -n peterson.5.net ../not_request_then_eventually_enter.mcf out.pbes

# Quotienting with approximation on intermediate formulae
formulaquotient -v -IPSFNA -n peterson.5.net ../not_request_then_eventually_enter.mcf out.pbes

# Run a PBES solver to solve the generated PBES
pbessolve -v out.pbes
```


### Comparable analysis using standard mCRL2 tools

```bash
# Linearise the specification
mcrl22lps -f -lregular2 -n ../peterson.5.mcrl2 peterson.5.lps
# Generate a PBES from the specification and a formula
lps2pbes -f ../not_request_then_eventually_enter.mcf peterson.7.lps peterson.5.pbes

# Run a PBES solver to solve the generated PBES
pbessolve -v peterson.5.pbes
```


## Version for two parties

### How we obtained the specification

- Download the original [peterson.mcrl2](https://raw.githubusercontent.com/jkeiren/paritygame-generator/master/cases/modelchecking/specs/mcrl2/peterson.mcrl2)
- Move the `act` declarations to abote the `proc` declarations;
- Replace `'` with `0`
- Add action `internal` to the `act` declaration and the `allow` and `hide` blocks
- Replace `tau` with `internal`
- Declare the initial process with `init hide(..., allow(..., comm(..., P1 || ...)))`

Instructions to obtain the patched version:

```bash
mkdir data
cd data
wget -O peterson.mcrl2.orig https://raw.githubusercontent.com/jkeiren/paritygame-generator/master/cases/modelchecking/specs/mcrl2/peterson.mcrl2
patch peterson.mcrl2.orig -i ../peterson.mcrl2-pmc.patch -o peterson.mcrl2
```

[Herlihy & Shavit (2008): The Art of Multiprocessor Programming]: https://books.google.nl/books?id=vfvPrSz7R7QC
[Raynal (2013): Concurrent Programming: Algorithms, Principles, and Foundations]: https://doi.org/10.1007/978-3-642-32027-9
