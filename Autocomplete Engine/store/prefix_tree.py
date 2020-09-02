"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type:
        A string that stores which method the aggregate weight is calculated
    num_leaves:
        An int that stores the number of leaves that this tree is an ancestor of
    total_weight:
        The sum of all weights of the leaves that this tree is an ancestor of.
        Only used for the when calculating average weight.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str
    num_leaves: int
    total_weight: float
    leaves: List

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self.weight_type = weight_type
        self.num_leaves = 0
        self.total_weight = 0.0

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter.
        """
        return self.num_leaves

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        done = False
        found = False
        if self.is_empty():
            self.add_on_prefix(value, weight, prefix, 0)
            self.add_weight(weight, False)
        elif self.value == prefix:
            for subtree in self.subtrees:
                if subtree.value == value:
                    self.add_weight(weight, True)
                    subtree.add_weight(weight, True)
                    found = True
                    break
            if not found:
                self.add_weight(weight, False)
                self.add_on_prefix(value, weight, prefix, len(self.subtrees))
        else:
            for subtree in self.subtrees:
                if prefix[0:len(subtree.value)] == subtree.value:
                    store_num_leaves = subtree.num_leaves
                    subtree.insert(value, weight, prefix)
                    if store_num_leaves != subtree.num_leaves:
                        self.add_weight(weight, False)
                    else:
                        self.add_weight(weight, True)
                    done = True
                    break
            if not done:
                index = 0
                for subtree in self.subtrees:
                    if weight > subtree.weight:
                        break
                    index += 1
                self.add_weight(weight, False)
                self.add_on_prefix(value, weight, prefix, index)
        self.weight_sort()

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        tree = self.search_for_prefix(prefix)
        leaves = tree.search_for_leaves()
        total_weight_remove = 0
        total_leaves_remove = 0
        for leaf in leaves:
            total_weight_remove += leaf[1]
            total_leaves_remove += 1
        self.update_weight_to_prefix \
            (prefix, total_weight_remove, total_leaves_remove)
        self.weight_sort()

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Precondition:
            limit is None or limit > 0
        """
        lit = True
        if limit is None:
            lit = False
        store = self.search_for_prefix(prefix)
        if store is not None:
            leaves = store.search_for_leaves()
            if lit:
                leaves = leaves[:limit]
            for index in range(len(leaves) - 1):
                for index2 in range(0, len(leaves) - index - 1):
                    if leaves[index2][1] < leaves[index2 + 1][1]:
                        leaves[index2], leaves[index2 + 1] = \
                            leaves[index2 + 1], leaves[index2]
            return leaves
        return []

    def add_weight(self, weight: float, is_leaf: bool) -> None:
        """Increases the weight of the tree"""
        if not is_leaf:
            self.num_leaves += 1
        if self.weight_type == 'sum':
            self.weight += weight * 1.0
            self.total_weight += weight * 1.0
        elif self.weight_type == 'average':
            self.total_weight += weight * 1.0
            self.weight = self.total_weight / self.num_leaves * 1.0

    def update_weight_to_prefix(self, prefix: List, total_weight: float,
                                total_leaves: int) -> None:
        """
        Updates all weights in a tree to a given subtree
        with a value equal to the prefix
        """
        if self.is_empty():
            return None
        elif self.value == prefix:
            self.value = []
            self.weight = 0
            self.subtrees = []
        else:
            if self.weight_type == 'sum':
                self.weight -= total_weight
                self.num_leaves -= total_leaves
            elif self.weight_type == 'average':
                self.total_weight -= total_weight
                self.num_leaves -= total_leaves
                if self.total_weight == 0:
                    self.weight = 0
                else:
                    self.weight = self.total_weight / self.num_leaves * 1.0
            if self.is_empty():
                self.subtrees = []
            else:
                for subtree in self.subtrees:
                    if prefix[0:len(subtree.value)] == subtree.value:
                        subtree.update_weight_to_prefix \
                            (prefix, total_weight, total_leaves)
                new_subtrees = []
                for subtree in self.subtrees:
                    if not subtree.is_empty():
                        new_subtrees.append(subtree)
                self.subtrees = new_subtrees

        return None
    def update_weight(self) -> None:
        """Update the weight of the tree
        """
        new_subtrees = []
        for subtree in self.subtrees:
            if not subtree.is_empty():
                new_subtrees.append(subtree)
        self.subtrees = new_subtrees
        if not self.subtrees:
            leaves = []
        else:
            leaves = self.search_for_leaves()
        if not leaves:
            self.value = []
            self.weight = 0.0
            self.subtrees = []
        else:
            self.weight = 0.0
            self.num_leaves = 0
            self.total_weight = 0.0
            if self.weight_type == 'sum':
                for leaf in leaves:
                    self.num_leaves += 1
                    self.weight += leaf[1]
                    self.total_weight += leaf[1]
            elif self.weight_type == 'average':
                for leaf in leaves:
                    self.total_weight += leaf[1]
                    self.num_leaves += 1
                self.weight = self.total_weight / self.num_leaves

    def find_num_leaves(self) -> None:
        """
        finds the total number of leaves by checking the number of leaves
        of its subtrees
        """
        if self.is_empty():
            return 0
        else:
            total_leaves = 0
            for subtree in self.subtrees:
                total_leaves += subtree.num_leaves
        return total_leaves

    def add_on_prefix(self, value: Any, weight: float, prefix: List,
                      index: int) -> None:
        """ Creates a list of incrementing prefix trees and the value at the end
            It then places the first prefix tree of the list in the list of
            subtrees at the index provided.
        """
        lst = []
        for i in range(len(self.value) + 1, len(prefix) + 1):
            new_spt = SimplePrefixTree(self.weight_type)
            new_spt.set_info(prefix[:i], weight, [])
            lst.append(new_spt)
        leaf_spt = SimplePrefixTree(self.weight_type)
        leaf_spt.set_info(value, weight, [])
        lst.append(leaf_spt)
        for i in range(len(lst) - 1):
            lst[i].subtrees.append(lst[i + 1])
        self.subtrees.insert(index, lst[0])

    def set_info(self, value: Any, weight: float, subtrees: List) -> None:
        """
        manually sets the parameters of the tree
        """
        self.value = value
        self.weight = weight * 1.0
        self.subtrees = subtrees
        self.num_leaves = 1
        self.total_weight = weight * 1.0

    def weight_sort(self) -> None:
        """
        Sorts the subtrees of this tree in  descending order by weight
        """
        index = 0
        while index < len(self.subtrees) - 1:
            for index2 in range(0, len(self.subtrees) - 1):
                if self.subtrees[index2].weight < \
                        self.subtrees[index2 + 1].weight:
                    self.subtrees[index2], self.subtrees[index2 + 1] = \
                        self.subtrees[index2 + 1], self.subtrees[index2]
            index += 1

    def search_for_prefix(self, prefix: List) -> Optional[SimplePrefixTree]:
        """
        Searches for a tree which has a value equal to the prefix and returns it
        """
        if self.is_empty():
            return None
        elif self.value == prefix:
            return self
        elif not prefix[0:len(self.value)] == self.value:
            return None
        else:
            for subtree in self.subtrees:
                store = subtree.search_for_prefix(prefix)
                if store is not None:
                    return store
            return None

    def search_for_leaves(self) -> Optional[List[Tuple[str, float]]]:
        """
        Finds all the leavves of this tree
        """
        if self.is_leaf():
            return [(self.value, self.weight)]
        elif self.is_empty():
            return None
        else:
            leaves = []
            for subtree in self.subtrees:
                store = subtree.search_for_leaves()
                for item in store:
                    if item is not None:
                        leaves.append(item)
            return leaves

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """

    # value: Optional[Any]
    # weight: float
    # subtrees: List[CompressedPrefixTree]
    # weight_type: str
    # num_leaves: int
    # total_weight: float

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        SimplePrefixTree.__init__(self, weight_type)

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        return self.num_leaves

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        found = False
        if self.is_empty():
            self.add_weight(weight, False)
            self.add_leaf(value, weight, prefix, 0)
        elif self.value == prefix:
            for subtree in self.subtrees:
                if subtree.value == value:
                    self.add_weight(weight, True)
                    subtree.add_weight(weight, True)
                    found = True
                    break
            if not found:
                self.add_weight(weight, False)
                self.add_on_prefix(value, weight, prefix, len(self.subtrees))
        else:
            self.comp_insert_help(value, weight, prefix)

    def comp_insert_help(self, value: Any, weight: float, prefix: List) -> None:
        """
        A helper method for the compressed tree insert method
        """
        done = False
        index_sub = 0
        for subtree in self.subtrees:
            match = True
            match_len = len(self.value)
            if not isinstance(subtree.value, List):
                match = False
            while match and (match_len != len(subtree.value) and
                             match_len != len(prefix)):
                if subtree.value[match_len] == prefix[match_len]:
                    match_len += 1
                elif match_len == len(self.value):
                    match = False
                    break
                else:
                    break
            if match:
                if match_len == len(subtree.value):
                    store_num_leaves = subtree.num_leaves
                    subtree.insert(value, weight, prefix)
                    if store_num_leaves != subtree.num_leaves:
                        self.add_weight(weight, False)
                    else:
                        self.add_weight(weight, True)
                else:
                    self.add_weight(weight, False)
                    new_prefix = CompressedPrefixTree(self.weight_type)
                    new_prefix.set_info(prefix[:match_len], 1, [])
                    new_prefix.subtrees.append(subtree)
                    new_prefix.add_leaf(value, weight, prefix, 1)
                    new_prefix.update_weight()
                    self.subtrees[index_sub] = new_prefix
                    self.weight_sort()
                done = True
                break
            index_sub += 1
        if not done:
            index = 0
            for subtree in self.subtrees:
                if weight > subtree.weight:
                    break
                index += 1
            self.add_weight(weight, False)
            self.add_leaf(value, weight, prefix, index)

    def search_for_prefix(self, prefix: List) -> Optional[SimplePrefixTree]:
        """
        Searches for a tree which has a value equal to the prefix and returns it
        :param prefix: A list which identifies a tree's value
        :return: the entire tree that is has the value indicated by 'prefix'
        """
        if self.is_empty():
            return None
        elif self.value[0:len(prefix)] == prefix and self.value != []:
            return self
        elif not prefix[0:len(self.value)] == self.value:
            return None
        else:
            for subtree in self.subtrees:
                store = subtree.search_for_prefix(prefix)
                if store is not None:
                    return store
            return None

    def add_leaf(self, value: Any, weight: float, prefix: List,
                 index: int) -> None:
        """ Creates a list of incrementing prefix trees and the value at the end
            It then places the first prefix tree of the list in the list of
            subtrees at the index provided.
        """
        leaf_spt = CompressedPrefixTree(self.weight_type)
        leaf_spt.set_info(value, weight, [])
        if self.value != prefix:
            prefix_spt = CompressedPrefixTree(self.weight_type)
            prefix_spt.set_info(prefix, weight, [leaf_spt])
            self.subtrees.insert(index, prefix_spt)
        else:
            self.subtrees.insert(index, leaf_spt)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
