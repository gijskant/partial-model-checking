# Example: two processes

## Prepare

```bash
mkdir data
cd data
../../../../scripts/mcrl22network.py ../example.mcrl2
```

## Run

```bash
# Quotienting without approximation on intermediate formulae
formulaquotient -v -IPS -nexample.net ../reach.mcf example.reach.pbes

# Quotienting with approximation on intermediate formulae
formulaquotient -v -IPSFN -nexample.net ../reach.mcf example.reach.pbes
```
