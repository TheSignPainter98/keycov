from .util import fst, iconcat, mult, snd
from copy import copy
from functools import reduce
from re import match
from typing import List, Set, Tuple

def get_covering_sets(to_cover:Tuple[str, List[int]], sets:Set[Tuple[str, List[int]]]) -> List[Tuple[str, List[int]]]:
    # Represent each layout as the product of the primes which represent its keys
    primed_to_cover = (to_cover[0], reduce(mult, to_cover[1], 1))
    primed_sets = list(map(lambda s: (s[0], 1, reduce(mult, s[1], 1)), sets))

    # Set of tuples containing the remainder and set of currently chosen keysets (as a number)
    seen:Set[Tuple[int, int]] = set()
    ##
    # @brief Perform a depth-first search on the set to cover,k
    #
    # @param r:int                  Uncovered remainder
    # @param cp:int                 Current path number
    # @param csp:int                Covering-set number
    # @param csns:[str]             Covering-set member names
    # @param psets:List[Tuple[str   Primed candidate sets
    #
    # @return
    def primes_dfs(r:int, cp:int, csp:int, csns:[str], psets:List[Tuple[str, int, int]]) -> [[str]]:
        seen.add((r, cp))
        if r == 1:
            return [csns]
        elif psets == []:
            return []

        child_covering_sets:[str] = []
        for n,p,kn in psets:
            r2:int = r // gcd(r, kn)
            cp2:int = cp * p
            csp2:int = csp * kn
            # Explore beneficial unexplored children
            if r != r2 and (r2, cp2) not in seen:
                psets2:List[Tuple[str, int, int]] = copy(psets)
                psets2.remove((n,p,kn))
                child_covering_sets.extend(primes_dfs(r2, cp2, csp2, csns + [n], psets2))
        return child_covering_sets

    # Perform dfs over covering sets
    covering_sets:[str] = primes_dfs(primed_to_cover[1], 1, 1, [], primed_sets)

    # Reunite set names with their contents
    set_dict:dict = dict(sets)
    return list(map(lambda c: list(map(lambda s: (s, set_dict[s]), c)), sorted(covering_sets)))

def get_uncovered(to_cover:Tuple[str, List[int]], sets:Set[Tuple[str, List[int]]]) -> List[Tuple[str, List[dict]]]:
    keys_to_cover:[int] = to_cover[1]
    uncovered:dict = { key: 0 for key in keys_to_cover }
    for key in keys_to_cover:
        uncovered[key] += 1

    for _,keys in sets:
        for key in keys:
            if key in uncovered and uncovered[key] >= 1:
                uncovered[key] -= 1

    return list(map(fst, sorted(filter(lambda p: p[1] > 0, uncovered.items()), key=snd)))

def gcd(a:int, b:int) -> int:
    while b != 0:
        (a, b) = (b, a % b)
    return a
