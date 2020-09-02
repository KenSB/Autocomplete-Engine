import csv
"""CSC148 Assignment 2: Autocomplete engines

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This file contains starter code for the three different autocomplete engines
you are writing for this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
import csv
from typing import Any, Dict, List, Optional, Tuple

from melody import Melody
from prefix_tree import SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines (Task 4)
################################################################################
class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a text file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one alphanumeric character, it is inserted into the
        Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given a weight of one.
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight (because of how Autocompleter.insert works).
        """
        # We've opened the file for you here. You should iterate over the
        # lines of the file and process them according to the description in
        # this method's docstring.
        with open(config['file'], encoding='utf8') as f:
            pass

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        pass

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

# lst2 = [1,2,3]
# lst1 = [1,2,3,4,5,6,7,8]
# print(lst1[0:len(lst2)] == lst2)
# print(lst1[:4])
# lst3 = []
# lst3.append('a')
# lst3.append('b')
# lst3.append('c')
# print(lst3)
#
# lst = [('pig',2),('cow',1),('meow',10),('boop',6),('meep',100)]
#
# for index in range(len(lst) - 1):
#     for index2 in range(0, len(lst) - index - 1):
#         if lst[index2][1] < lst[index2 + 1][1]:
#             lst[index2], lst[index2 + 1] = \
#                 lst[index2 + 1], lst[index2]
# print(lst)
#
# string = "*2sd2340 9u1u )(((((( swwww"
# print(' '.join(e for e in string if e.isalnum()))
#
# alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
#         'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
#         'y', 'z', ' ']
# line = '“…” When Lawrence drew his dagger, the girl’s smile disappeared. Her'
# side = line.lower()
# s = line.lower()
# lst_line = []
# for char in side:
#     if char not in alpha:
#         s = s.replace(char+'', '')
# print(s)

with open('data\sample_arrivals.csv') as csvfile:
    reader = csv.reader(csvfile)
    for line in reader:
        print(line)
