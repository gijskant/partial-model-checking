#~/bin/bash
if [ "$#" -lt 1 ]; then
  echo "Usage: $(basename "$0") <property.mcf>"
  exit
fi
filename=$(basename "$1")
extension="${filename##*.}"
filename="${filename%.*}"
cmd="formulaquotient -vIPSFN -nexample.net $1 example.${filename}.pbes"

echo $cmd
exec $cmd
