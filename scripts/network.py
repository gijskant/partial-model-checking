#! /usr/bin/env python3
import os
import sys

bullet = "inactive"


def print_vector(components, types, vector_elements):
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
                    st = st + ": " + t
                result.append(st)
        else:
            sys.exit("No 'comm' in vector entry: " + str(v))
    txt += str(len(components)) + '\n'
    txt += "{" + '\n'
    for r in result:
        txt += "  ( " + r + " )" + '\n'
    txt += "}"
    return txt


def parse_network(network_filename):
    reading_filenames = False
    filenames = []
    components = []
    with open(network_filename) as network_file:
        for line in network_file:
            line = line.strip()
            # print "Line:", l
            if reading_filenames:
                if line == "synchronization_vector":
                    # print "Stop reading filenames"
                    break
                else:
                    filenames.append(line)
                    components.append(os.path.splitext(line)[0])
            else:
                if line == "lps_filenames":
                    # print "Start reading filenames"
                    reading_filenames = True
    return filenames, components


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        (lps_files, network_components) = parse_network(filename)
        print(network_components)
