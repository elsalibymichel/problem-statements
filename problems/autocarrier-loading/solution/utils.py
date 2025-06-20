# Some utility functions for the project
import random
from typing import Iterable, Dict, Union, List

JSONValue = Union[
    None,
    bool,
    int,
    float,
    str,
    List['JSONValue'],
    Dict[str, 'JSONValue']
]

def sparse_fisher_yates_iter(n: int) -> Iterable[int]:
    """
        Generate a random permutation of indices from 0 to n-1 using a sparse Fisher-Yates shuffle.
        :param n: The number of elements to permute.
        :return: An iterable yielding indices in a random order.
        This implementation uses a dictionary to store the mapping of indices, which saves memory compared to a full array, especially for large n. It yields indices in a random order.
    """
    p: Dict[int, int] = dict()
    for i in range(n - 1, -1, -1):
        r = random.randrange(i + 1)
        yield p.get(r, r)
        if i != r:
            # p[r] = p.pop(i, i) # saves memory, takes time
            p[r] = p.get(i, i)  # lazy, but faster

def random_indexes_iterator(n: int) -> Iterable[int]:
    """
        Generate a random permutation of indices from 0 to n-1.
        :param n: The number of elements to permute.
        :return: An iterable yielding indices in a random order.
        This function uses the sparse Fisher-Yates shuffle.
    """
    return sparse_fisher_yates_iter(n)

def random_pairs_iterator(n: int, m: int) -> Iterable[tuple[int, int]]:
    """
        Generate random pairs of indices from two ranges.
        :param n: The number of elements in the first range (0 to n-1).
        :param m: The number of elements in the second range (0 to m-1).
        :return: An iterable yielding tuples of indices (i, j) where i is from the first range and j is from the second range.
        This function generates random pairs of indices using the sparse Fisher-Yates shuffle for both dimensions.
    """
    for v in random_indexes_iterator(n * m):
            i = v // m
            j = v % m                
            yield (i, j)


