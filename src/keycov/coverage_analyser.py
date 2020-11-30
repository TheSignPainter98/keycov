from .util import fst, iconcat, mult, snd
from copy import copy
from functools import reduce
from math import ceil, sqrt, gcd as hcf
from re import match
from typing import List, Set, Tuple

def get_covering_sets(to_cover:Tuple[str, List[dict]], sets:Set[Tuple[str, List[dict]]]) -> List[Tuple[str, List[dict]]]:
    # Generate a unique prime for each unique key
    prime:iter = primes()
    seen_keys:dict = {}
    for layout in sets + [to_cover]:
        for key in layout[1]:
            if key['serialised'] not in seen_keys:
                seen_keys[key['serialised']] = next(prime)

    # Represent each layout as the product of the primes which represent its keys
    primed_to_cover = (to_cover[0], reduce(mult, map(lambda k: seen_keys[k['serialised']], to_cover[1]), 1))
    primed_sets = list(map(lambda s: (s[0], reduce(mult, map(lambda k: seen_keys[k['serialised']], s[1]), 1)), sets))

    seen:set = set()
    def primes_dfs(r:int, csp:int, csns:[str], psets:List[Tuple[str, int]]) -> [[str]]:
        seen.add(csp)
        if r == 1:
            return [csns]
        elif psets == []:
            return []

        child_covering_sets:[str] = []
        for s in psets:
            r2:int = r // gcd(r, s[1])
            csp2:int = csp * s[1]
            # Explore beneficial unexplored children
            if r != r2 and csp2 not in seen:
                psets2:List[Tuple[str, int]] = copy(psets)
                psets2.remove(s)
                child_covering_sets.extend(primes_dfs(r2, csp2, csns + [s[0]], psets2))
        return child_covering_sets

    # Perform dfs over covering sets
    covering_sets:[str] = primes_dfs(primed_to_cover[1], 1, [], primed_sets)

    # Reunite set names with their contents
    set_dict:dict = dict(sets)
    return list(map(lambda c: list(map(lambda s: (s, set_dict[s]), c)), sorted(covering_sets)))

def get_uncovered(to_cover:Tuple[str, List[dict]], sets:Set[Tuple[str, List[dict]]]) -> List[Tuple[str, List[dict]]]:
    keys_to_cover:[str] = list(map(lambda c: c['serialised'], to_cover[1]))
    uncovered:dict = { key: 0 for key in keys_to_cover }
    for key in keys_to_cover:
        uncovered[key] += 1

    for _,keys in sets:
        for key in map(lambda k: k['serialised'], keys):
            if key in uncovered and uncovered[key] >= 1:
                uncovered[key] -= 1

    return list(map(fst, sorted(filter(lambda p: p[1] > 0, uncovered.items()), key=snd)))

def gcd(a:int, b:int) -> int:
    while b != 0:
        (a, b) = (b, a % b)
    return a

def primes() -> [int]:
    i:int = 3
    while True:
        yield i
        while True:
            i += 2
            if is_prime(i):
                break

def is_prime(n:int) -> bool:
    # Assume n >= 3
    for i in range(2, ceil(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True
