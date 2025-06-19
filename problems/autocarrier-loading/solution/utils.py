# Some utility functions for the project
import random
from typing import Iterable, Dict

def sparse_fisher_yates_iter(n: int) -> Iterable[int]:
    p: Dict[int, int] = dict()
    for i in range(n - 1, -1, -1):
        r = random.randrange(i + 1)
        yield p.get(r, r)
        if i != r:
            # p[r] = p.pop(i, i) # saves memory, takes time
            p[r] = p.get(i, i)  # lazy, but faster

def random_index_iterator(n: int) -> Iterable[int]:
    """Generate a random permutation of indices from 0 to n-1."""
    return sparse_fisher_yates_iter(n)

def random_pair_iterator(n: int, m: int) -> Iterable[tuple[int, int]]:
    """Generate random pairs of indices from two ranges."""
    for v in random_index_iterator(n * m):
            i = v // m
            j = v % m                
            yield (i, j)

