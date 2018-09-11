# Example: Peterson's mutual exclusion algorithm

Example taken from Jeroen Keiren's 
[parity game benchmarks repository](https://github.com/jkeiren/paritygame-generator),
from the collection of model checking problems, with a few modifications.

- Download the original [peterson.mcrl2](https://raw.githubusercontent.com/jkeiren/paritygame-generator/master/cases/modelchecking/specs/mcrl2/peterson.mcrl2)
- Move the `act` declarations to abote the `proc` declarations;
- Replace `'` with `0`
- Add action `internal` to the `act` declaration and the `allow` and `hide` blocks
- Replace `tau` with `internal`
- Declare the initial process with `init hide(..., allow(..., comm(..., P1 || ...)))`

## Prepare

```bash
mkdir data
cd data
wget -O peterson.mcrl2.orig https://raw.githubusercontent.com/jkeiren/paritygame-generator/master/cases/modelchecking/specs/mcrl2/peterson.mcrl2
patch peterson.mcrl2.orig -i ../peterson.mcrl2-pmc.patch -o peterson.mcrl2
../../../scripts/mcrl22network.py peterson.mcrl2
```

## Run

```bash
# Quotienting without approximation on intermediate formulae
formulaquotient -v -IPS -n peterson.net ../not_request_then_eventually_enter.mcf out.pbes

# Quotienting with approximation on intermediate formulae
formulaquotient -v -IPSFNA -n peterson.net ../not_request_then_eventually_enter.mcf out.pbes
```
