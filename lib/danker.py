#!/usr/bin/env python3

#    danker - PageRank on Wikipedia/Wikidata
#    Copyright (C) 2017  Andreas Thalhammer
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
danker
"""
import sys
import time
import argparse

def _conv_int(string):
    """
    Helper function to optimize memory usage.
    """
    if string.isdigit():
        return int(string)
    return string

def init(left_sorted, start_value, smallmem):
    """
    Read left_sorted link file and initialization steps.
    """
    dictionary_i_1 = {}
    previous = -1
    current_count = 1
    with open(left_sorted, encoding="utf-8") as ls_file:
        for line in ls_file:
            current = _conv_int(line.split("\t")[0].strip())
            receiver = _conv_int(line.split("\t")[1].strip())

            # take care of inlinks
            if not smallmem:
                data = dictionary_i_1.get(receiver, (0, start_value, []))
                data[2].append(current)
                dictionary_i_1[receiver] = data[0], data[1], data[2]

            # take care of counts
            if current == previous:
                # increase counter
                current_count = current_count + 1
            else:
                if previous != -1:
                    # store previousQID and reset counter
                    prev = dictionary_i_1.get(previous, (0, start_value, []))
                    dictionary_i_1[previous] = current_count, prev[1], prev[2]
                    current_count = 1
            previous = current

        # take care of last item
        if previous != -1:
            prev = dictionary_i_1.get(previous, (0, start_value, []))
            dictionary_i_1[previous] = current_count, prev[1], prev[2]
    return dictionary_i_1

def danker_smallmem(dictionary_i_1, right_sorted, iterations, damping, start_value):
    """
    Compute PageRank with right sorted file.
    """
    dictionary_i = {}
    for i in range(0, iterations):
        print(str(i + 1) + ".", end="", flush=True, file=sys.stderr)
        previous = 0
        with open(right_sorted, encoding="utf-8") as rs_file:
            for line in rs_file:
                current = _conv_int(line.split("\t")[1].strip())
                if previous != current:
                    dank = 1 - damping
                current_dank = dictionary_i_1.get(current, (0, start_value))
                in_link = _conv_int(line.split("\t")[0].strip())
                in_dank = dictionary_i_1.get(in_link)
                dank = dank + (damping * in_dank[1] / in_dank[0])
                dictionary_i[current] = current_dank[0], dank
                previous = current

        # after each iteration, fix nodes that don't have inlinks
        for i in dictionary_i_1.keys() - dictionary_i.keys():
            dictionary_i[i] = dictionary_i_1[i][0], 1 - damping
        dictionary_i_1 = dictionary_i
        dictionary_i = {}

    print("", file=sys.stderr)
    return dictionary_i_1

def danker_bigmem(dictionary_i_1, iterations, damping):
    """
    Compute PageRank with big memory option.
    """
    dictionary_i = {}
    for i in range(0, iterations):
        print(str(i + 1) + ".", end="", flush=True, file=sys.stderr)
        for i in dictionary_i_1:
            current = dictionary_i_1.get(i)
            dank = 1 - damping
            for j in current[2]:
                in_dank = dictionary_i_1.get(j)
                dank = dank + (damping * in_dank[1] / in_dank[0])
            dictionary_i[i] = current[0], dank, current[2]
        dictionary_i_1 = dictionary_i
        dictionary_i = {}
    print("", file=sys.stderr)
    return dictionary_i_1

def main():
    """
    Execute main program.
    """
    parser = argparse.ArgumentParser(description='danker PageRank.')
    parser.add_argument('left_sorted')
    parser.add_argument('--right_sorted')
    parser.add_argument('damping', type=float)
    parser.add_argument('iterations', type=int)
    parser.add_argument('start_value', type=float)
    a = parser.parse_args()
    start = time.time()
    
    dictionary_i_1 = init(a.left_sorted, a.start_value, a.right_sorted)
    
    if a.right_sorted:
        dictionary_i = danker_smallmem(dictionary_i_1, a.right_sorted, a.iterations, a.damping, a.start_value)
    else:
        dictionary_i = danker_bigmem(dictionary_i_1, a.iterations, a.damping)
    
    for i in dictionary_i:
        print("{0}\t{1:.17g}".format(i, dictionary_i[i][1]))
    print("Computation of PageRank on '{0}' took {1:.2f} seconds.".format(
        a.left_sorted, time.time() - start), file=sys.stderr)


if __name__ == '__main__':
    main()
