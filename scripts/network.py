#! /usr/bin/env python
import os
import sys
import re

bullet = "inactive"

def print_vector(components, types, vector_elements):
  i = 1
  txt = ''
  result = []
  for v in vector_elements:
    s = ""
    for k in components:
      if k in v:
        s += v[k] + ", "
      else:
        s += bullet + ", "
    if "comm" in v:
      for t in types[v["comm"]]:
        t = t.strip()
        st = s + v["comm"]
        if not t == "":
          st = st +": "+t
        result.append(st)
    else:
      sys.exit("No 'comm' in vector entry: " + str(v))
      s += "tau" + str(i)
      i += 1
      result.append(s)
  txt += str(len(components)) + '\n'
  txt += "{" + '\n'
  for r in result:
    txt += "  ( " + r + " )" + '\n'
  txt += "}"
  return txt

def parse_network(filename):
  reading_filenames = False
  filenames = []
  components = []
  with open(filename) as f:
    for l in f:
      l = l.strip()
      # print "Line:", l
      if(reading_filenames):
        if l == "synchronization_vector":
          # print "Stop reading filenames"
          break
        else:
          filenames.append(l)
          components.append(os.path.splitext(l)[0])
      else:
        if l == "lps_filenames":
          # print "Start reading filenames"
          reading_filenames = True
  return (filenames, components)

if __name__ == '__main__':
  if len(sys.argv) > 1:
    filename = sys.argv[1]
    (lps_files, components) = parse_network(filename)
    print components
