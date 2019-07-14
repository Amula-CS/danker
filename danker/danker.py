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
#import memory_profiler

class InputNotSortedException(Exception):
    _MESSAGE = 'Input file "{0}" is not correctly sorted. "{1}" after "{2}"'

    def __init__(self, file_name, line1, line2):
        message = self._MESSAGE.format(file_name, line1, line2)
        Exception.__init__(self, message)

def _conv_int(string):
    """
    Helper function to optimize memory usage.
    """
    if string.isdigit():
        return int(string)
    return string

def _get_std_list(smallmem, start_value):
    """
    Helper function to return standard list for smallmem vs bigmem.
    """
    if smallmem:
        return [0, start_value, start_value, False]
    return [0, start_value, start_value, []]

def init(left_sorted, start_value, smallmem):
    """
    This function creates the data structure for PageRank computation by
    indexing every node. Main indexing steps include setting the starting
    value as well as counting the number of outgoing links for each node.

    :param left_sorted: A tab-separated link file that is sorted by the
                        left column.
    :param start_value: The PageRank starting value.
    :param smallmem: This value is interpreted as a boolean that indicates
                     whether the indexing should be done for
                     :func:`danker_smallmem` (file iteration) or
                     :func:`danker_bigmem` (in-memory). Default is "False".
    :returns: Dictionary with each key referencing a node. The value is a
              list with the following contentsi - depending on the smallmem
              parameter and the intended use:

              * :func:`danker_bigmem` [link_count:int, start_value:float,
                start_value:float, linked_pages:list]

              * :func:`danker_smallmem` [link_cout:int, start_value:float,
                start_value:float, touched_in_1st_iteration:boolean]
    """
    dictionary = {}
    previous = None
    current_count = 1
    with open(left_sorted, encoding="utf-8") as ls_file:
        for line in ls_file:
            current = _conv_int(line.split("\t")[0].strip())
            receiver = _conv_int(line.split("\t")[1].strip())

            # take care of inlinks
            if not smallmem:
                data = dictionary.setdefault(receiver, _get_std_list(smallmem, start_value))
                data[3].append(current)

            # take care of counts
            if current == previous:
                # increase counter
                current_count = current_count + 1
            else:
                if previous:
                    # make sure input is correctly sorted
                    if current < previous:
                        raise InputNotSortedException(left_sorted, current, previous)
                    # store previous Q-ID and reset counter
                    prev = dictionary.get(previous, _get_std_list(smallmem, start_value))
                    dictionary[previous] = [current_count] + prev[1:]
                    current_count = 1
            previous = current

        # take care of last item
        if previous:
            prev = dictionary.get(previous, _get_std_list(smallmem, start_value))
            dictionary[previous] = [current_count] + prev[1:]
    return dictionary

#@profile
def danker_smallmem(dictionary, right_sorted, iterations, damping, start_value):
    """
    Compute PageRank with right sorted file.

    :param dictionary: Python dictionary created with :func:`init`
                       (smallmem set to True).
    :param right_sorted: The same tab-separated link file that was used for
                         :func:`init` sorted by the right column.
    :param iterations: The number of PageRank iterations.
    :param damping: The PageRank damping factor.
    :param start_value: The PageRank starting value (same as was used for
                        :func:`init`).
    :return:
    """
    for iteration in range(0, iterations):
        print(str(iteration + 1) + ".", end="", flush=True, file=sys.stderr)
        previous = None

        # positions for i and i+1 result values (alternating with iterations).
        i_location = (iteration % 2) + 1
        i_plus_1_location = ((iteration + 1) % 2) + 1

        with open(right_sorted, encoding="utf-8") as rs_file:
            for line in rs_file:
                current = _conv_int(line.split("\t")[1].strip())
                if previous != current:
                    if previous and current < previous:
                        raise InputNotSortedException(right_sorted, current, previous)

                    # reset dank
                    dank = 1 - damping
                    # initialize in case of no outgoing links
                    dictionary.setdefault(current, _get_std_list(True, start_value))

                in_link = _conv_int(line.split("\t")[0].strip())
                in_dank = dictionary.get(in_link)
                dank = dank + (damping * in_dank[i_location] / in_dank[0])
                dictionary[current][i_plus_1_location] = dank
                previous = current

                # record current node as 'touched' (it has incoming links)
                if iteration == 0:
                    dictionary[current][3] = True

            # fix 'untouched' nodes (they do not have incoming links)
            if iteration == 0:
                for k in dictionary.keys():
                    if not dictionary[k][3]:
                        dictionary[k][i_plus_1_location] = 1 - damping
                        dictionary[k][i_location] = 1 - damping
    print("", file=sys.stderr)
    return dictionary

#@profile
def danker_bigmem(dictionary, iterations, damping):
    """
    Compute PageRank with big memory option.

    :param dictionary: Python dictionary created with :func:`init`
                       (smallmem set to False).
    :param iterations: The number of PageRank iterations.
    :param damping: The PageRank damping factor.
    :return:
    """
    for iteration in range(0, iterations):

        # positions for i and i+1 result values (alternating with iterations).
        i_location = (iteration % 2) + 1
        i_plus_1_location = ((iteration + 1) % 2) + 1

        print(str(iteration + 1) + ".", end="", flush=True, file=sys.stderr)
        for j in dictionary:
            current = dictionary.get(j)
            dank = 1 - damping
            for k in current[3]:
                in_dank = dictionary.get(k)
                dank = dank + (damping * in_dank[i_location] / in_dank[0])
            dictionary[j][i_plus_1_location] = dank
    print("", file=sys.stderr)
    return dictionary

#@profile
def _main():
    """
    Execute main program.
    """
    parser = argparse.ArgumentParser(description='danker PageRank.')
    parser.add_argument('left_sorted')
    parser.add_argument('--right_sorted')
    parser.add_argument('damping', type=float)
    parser.add_argument('iterations', type=int)
    parser.add_argument('start_value', type=float)
    args = parser.parse_args()
    start = time.time()
    dictionary = init(args.left_sorted, args.start_value, args.right_sorted)
    result_position = (args.iterations % 2) + 1
    if args.right_sorted:
        danker_smallmem(dictionary, args.right_sorted, args.iterations,
                        args.damping, args.start_value)
    else:
        danker_bigmem(dictionary, args.iterations, args.damping)
    print("Computation of PageRank on '{0}' with {1} took {2:.2f} seconds.".format(
        args.left_sorted, 'danker', time.time() - start), file=sys.stderr)

    for i in dictionary:
        print("{0}\t{1:.17g}".format(i, dictionary[i][result_position]))

if __name__ == '__main__':
    _main()
