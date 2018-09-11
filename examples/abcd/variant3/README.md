# Example: two processes

## Prepare

```bash
mkdir data
cd data
../../../../scripts/mcrl22network.py ../YXexample.mcrl2
```

## Run

```bash
# Quotienting without approximation on intermediate formulae
formulaquotient -v -IPS -n YXexample.net ../reach.mcf YXexample.reach.pbes

# Quotienting with approximation on intermediate formulae
formulaquotient -v -IPSFNA -n YXexample.net ../reach.mcf YXexample.reach.pbes
```
