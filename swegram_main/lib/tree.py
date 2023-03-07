"""Module to check if a sentence is a ud tree

"""
from collections import Counter
from typing import List, Union


def is_ud_tree(heads: List[int]) -> Union[bool, str]:
    """Check if a sentence is ud tree compatible"""
    children = list(range(1, len(heads) + 1))
    if 0 not in heads:
        return "Root is missing"
    if Counter(heads)[0] > 1:
        return "More than one root in sentence"
    if len(children) > len(set(children)):
        return "Same indeces for two nodes"

    for i in children:
        head = [heads[i-1]]
        while 0 not in head:
            if heads[head[-1] - 1] in head:
                return "Cycle Error"
            head.append(heads[head[-1] - 1])
        head = []
    return True
