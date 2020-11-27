from .util import add, concat, fst, snd, swp
from .coverage_analyser import get_covering_sets
from argparse import Namespace
from functools import reduce
from typing import List, Tuple

DEFAULT_VERBOSITY:int = 1

class AnalysisFailedError(Exception):
    def __init__(self, message:str):
        super()
        self.message = message

class AnalysisTypes:
    LOCAL:int = 0x1
    GLOBAL:int = 0x2
    INDIVIDUAL_KITS:int = 0x4
    INDIVIDUAL_KEEBS:int = 0x8
    ITERATE_KITS:int = 0x10
    ITERATE_KEEBS:int = 0x20

class FailedAnalysisResult:
    result:object
    def __init__(self, result):
        self.result = result

analyses:[dict] = [
    {
        'name': 'num_keebs',
        'pretty-name': 'Total keyboards',
        'description': 'Total number of keyboard layouts analysed',
    },
    {
        'name': 'num_kits',
        'pretty-name': 'Total kits',
        'description': 'Total number of kits analysed',
    },
    {
        'name': 'most_common_kit_keys',
        'pretty-name': 'Most common keys in kits',
        'description': 'Finds out the 10 keys which are the most common in the kits presented',
        'verbosity': 2
    },
    {
        'name': 'most_common_keeb_keys',
        'pretty-name': 'Most common keys in keyboards',
        'description': 'Finds out the 10 keys which are the most common in the target keyboard layouts presented',
        'verbosity': 2
    },
    {
        'name': 'count_units',
        'pretty-name': 'Total units',
        'description': 'Computes the total number of units present in a given layout',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KITS | AnalysisTypes.INDIVIDUAL_KEEBS
    },
    {
        'name': '~compute_covering_set',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.ITERATE_KITS | AnalysisTypes.ITERATE_KEEBS
    },
    {
        'name': 'exists_covering_set',
        'pretty-name': 'Is covered',
        'description': 'Describes for a keeb whether there exists a covering set of kits, or vice versa',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KITS | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~compute_covering_set'
        ]
    },
    {
        'name': 'number_of_covering_sets',
        'pretty-name': 'Number of covering sets',
        'description': 'The number of sets of kits which cover a given keyboard',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KITS | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~compute_covering_set'
        ]
    },
    {
        'name': '~count_covering_set_units',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~compute_covering_set'
        ]
    },
    {
        'name': '~covering_set_of_lowest_units',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~count_covering_set_units'
        ]
    },
    {
        'name': '~covering_set_of_lowest_units_surplus',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_units'
        ]
    },
    {
        'name': 'covering_set_of_lowest_units_surplus_amount',
        'pretty-name': 'Minimal-unit covering sets surplus',
        'description': 'Shows the least amount of surplus units (waste plastic) required by any set of kits which covers a particular keyboard',
        'verbosity': 1,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_units_surplus'
        ]
    },
    {
        'name': 'covering_set_of_lowest_units_surplus_value',
        'pretty-name': 'Minimal-unit covering set',
        'description': 'The set of kits with minimal surplus units which covers a particular keyboard',
        'verbosity': 3,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_units_surplus'
        ]
    },
    {
        'name': '~covering_set_cardinalities',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~compute_covering_set'
        ]
    },
    {
        'name': '~covering_set_of_lowest_cardinality',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_cardinalities'
        ]
    },
    {
        'name': 'covering_set_of_lowest_cardinality_amount',
        'pretty-name': 'Smallest covering set size',
        'description': 'The smallest number of kits required to cover a particular keyboard',
        'verbosity': 2,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_cardinality'
        ]
    },
    {
        'name': 'covering_set_of_lowest_cardinality_value',
        'pretty-name': 'Smallest covering set',
        'description': 'The smallest set of kits which covers a particular keyboard',
        'verbosity': 3,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_cardinality'
        ]
    },
    {
        'name': 'most_cumbersome_keyboard',
        'pretty-name': 'Keyboard requiring the most kits',
        'description': 'The keyboard which requires a customer to purchase the most kits in order to cover it',
        'requires': [
            '~covering_set_cardinalities'
        ]
    },
    {
        'name': 'most_wasteful_keyboard',
        'pretty-name': 'Keyboard with most surplus units to cover',
        'description': 'The keyboard which requires the most wasted units of plastic to cover',
        'requires': [
            '~covering_set_of_lowest_units'
        ]
    },
    {
        'name': 'least_used_kit',
        'pretty-name': 'Least-required kit',
        'description': 'The kit which is required in the fewest setups',
        'verbosity': 2,
        'requires': [
            '~compute_covering_set',
        ]
    },
    {
        'name': 'smallest_covering_kit_set_is_minimal_surplus_covering_kit_set',
        'pretty-name': 'Smallest-kit covering set is smallest unit covering set',
        'description': 'The covering set of kits for a keyboard which has the fewest total units also contains the fewest necessary kits',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'verbosity': 2,
        'requires': [
            '~covering_set_of_lowest_cardinality',
            '~covering_set_of_lowest_units',
        ]
    },
    {
        'name': 'all_keyboards_have_smallest_covering_kit_set_is_minimal_surplus_covering_kit_set',
        'pretty-name': 'Optimal units per kit',
        'description': 'Checks whether for each keyboard, the set of kits which covers it with the least surplus units, is also the smallest set of kits which covers it. Note that this checks for a locally optimal solution, whether the solution is the global optimum---more efficient kitting may still be possible but will require some re-arrangement.',
        'requires': [
            'smallest_covering_kit_set_is_minimal_surplus_covering_kit_set'
        ]
    },
    {
        'name': 'all_kits_covered',
        'pretty-name': 'All kits covered',
        'description': 'Checks whether every key in every kit is a part of some keyboard (and so not useless)',
        'requires': [
            'exists_covering_set',
        ]
    },
    {
        'name': 'all_keebs_covered',
        'pretty-name': 'All keyboards covered',
        'description': 'Checks whether every key in every keyboard is a part of some kit (and so not missing)',
        'requires': [
            'exists_covering_set',
        ]
    },
]

def num_keebs(_1:Namespace, _2:dict, target_layouts:[dict], _3:[dict]) -> int:
    return len(target_layouts)

def num_kits(_1:Namespace, _2:dict, _3:[dict], input_layouts:[dict]) -> int:
    return len(input_layouts)

def most_common_kit_keys(pargs:Namespace, _1:dict, target_layouts:[dict], _2:[dict]) -> [str]:
    return most_common_keys(target_layouts, pargs.output_list_cutoff)

def most_common_keeb_keys(pargs:Namespace, _1:dict, _2:[dict], input_layouts:[dict]) -> [str]:
    return most_common_keys(input_layouts, pargs.output_list_cutoff)

def most_common_keys(layouts:[dict], output_cutoff:int) -> [str]:
    key_occurrences:dict = count_key_occurrences(layouts)
    sorted_occurrences:[str] = list(map(lambda p: '%s (%s)' % p, sorted(key_occurrences.items(), key=swp)))

    if output_cutoff > 0:
        return sorted_occurrences[:output_cutoff]
    return sorted_occurrences

def count_key_occurrences(layouts:Tuple[str, List[dict]]) -> dict:
    occurrences:dict = {}
    for layout in layouts:
        for key in layout[1]:
            if key['pretty-name'] in occurrences:
                occurrences[key['pretty-name']] += 1
            else:
                occurrences[key['pretty-name']] = 1
    return occurrences

def count_units(_1:Namespace, _2:dict, layout:tuple) -> float:
    return get_total_units(layout)

def get_total_units(layout:Tuple[str, List[dict]]) -> float:
    return reduce(lambda a,b: a + b, map(get_units, layout[1]), 0.0)

def get_units(key:dict) -> float:
    considered_dims:[float] = [key['w'], key['h']]
    extra_dims:[float] = [key['w2'], key['h2']]
    if any(map(lambda v: v != 1, extra_dims)):
        considered_dims += extra_dims
    return max(considered_dims)

def compute_covering_set(pargs:Namespace, _:dict, keeb:Tuple[str, List[dict]], kits:List[Tuple[str, List[dict]]]) -> List[Tuple[str, List[dict]]]:
    covering_sets:List[Tuple[str, List[dict]]] = get_covering_sets(keeb, kits)
    if not covering_sets:
        return FailedAnalysisResult(covering_sets)
    return covering_sets

def exists_covering_set(_1:dict, coverage_data:dict, layout:[dict]) -> bool:
    return coverage_data['compute_covering_set'][layout[0]] != []

def all_keebs_covered(_1:dict, coverage_data:dict, keebs:List[Tuple[str, List[dict]]], _2:List[Tuple[str, List[dict]]]) -> bool:
    keeb_names:list = list(map(fst, keebs))
    return all(map(snd, filter(lambda p: p[0] in keeb_names, coverage_data['exists_covering_set'].items())))

def all_kits_covered(_1:dict, coverage_data:dict, _2:List[Tuple[str, List[dict]]], kits:List[Tuple[str, List[dict]]]) -> bool:
    kit_names:list = list(map(fst, kits))
    return all(map(snd, filter(lambda p: p[0] in kit_names, coverage_data['exists_covering_set'].items())))

def number_of_covering_sets(_1:dict, coverage_data:dict, layout:[dict]) -> int:
    return len(coverage_data['compute_covering_set'][layout[0]])

def count_covering_set_units(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> Tuple[str, List[dict]]:
    css:List[Tuple[str, List[dict]]] = coverage_data['compute_covering_set'][keeb[0]]
    return list(map(lambda cs: (reduce(add, map(lambda s: get_total_units(s), cs), 0.0), cs), css))

def covering_set_of_lowest_units(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> Tuple[str, List[dict]]:
    csus:List[Tuple[str, List[dict]]] = coverage_data['count_covering_set_units'][keeb[0]]
    return min(csus, key=fst)

def covering_set_of_lowest_units_surplus(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> float:
    cs:Tuple[float, List[Tuple[str, List[dict]]]] = coverage_data['covering_set_of_lowest_units'][keeb[0]]
    return (cs[0] - get_total_units(keeb), list(map(fst, cs[1])))

def covering_set_of_lowest_units_surplus_amount(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> [str]:
    return coverage_data['covering_set_of_lowest_units_surplus'][keeb[0]][0]

def covering_set_of_lowest_units_surplus_value(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> [str]:
    return coverage_data['covering_set_of_lowest_units_surplus'][keeb[0]][1]

def covering_set_cardinalities(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> float:
    css:List[Tuple[str, List[dict]]] = coverage_data['compute_covering_set'][keeb[0]]
    return list(map(lambda cs: (len(cs), cs), css))

def covering_set_of_lowest_cardinality(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> float:
    return min(coverage_data['covering_set_cardinalities'][keeb[0]], key=fst)

def covering_set_of_lowest_cardinality_amount(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> float:
    return coverage_data['covering_set_of_lowest_cardinality'][keeb[0]][0]

def covering_set_of_lowest_cardinality_value(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> [str]:
    return list(map(fst, coverage_data['covering_set_of_lowest_cardinality'][keeb[0]][1]))

def smallest_covering_kit_set_is_minimal_surplus_covering_kit_set(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> bool:
    smallest_covering_set:Set[Tuple[str, [dict]]] = set(map(fst, coverage_data['covering_set_of_lowest_cardinality'][keeb[0]][1]))
    minimal_surplus_covering_set:Set[Tuple[str, [dict]]] = set(map(fst, coverage_data['covering_set_of_lowest_units'][keeb[0]][1]))
    return smallest_covering_set == minimal_surplus_covering_set

def all_keyboards_have_smallest_covering_kit_set_is_minimal_surplus_covering_kit_set(_1:Namespace, coverage_data:dict, _2:[dict], _3:[dict]) -> bool:
    return all(coverage_data['smallest_covering_kit_set_is_minimal_surplus_covering_kit_set'].values())

def most_cumbersome_keyboard(_1:Namespace, coverage_data:dict, _2:[dict], _3:[dict]) -> str:
    lowest_cardinality_covering_sets:List[Tuple[int, str]] = list(map(lambda p: (p[1][0], p[0]), coverage_data['covering_set_of_lowest_cardinality'].items()))
    if lowest_cardinality_covering_sets == []:
        return None
    mck:Tuple[int, str] = max(lowest_cardinality_covering_sets, key=fst)
    return '%s (%d)' %(mck[1], mck[0])

def most_wasteful_keyboard(_1:Namespace, coverage_data:dict, _2:[dict], _3:[dict]) -> str:
    lowest_units_covering_sets:List[Tuple[float, str]] = list(map(lambda p: (p[1][0], p[0]), coverage_data['covering_set_of_lowest_units_surplus'].items()))
    if lowest_units_covering_sets == []:
        return None
    mwk:Tuple[int, str] = max(lowest_units_covering_sets, key=fst)
    return '%s (%.2f)' %(mwk[1], mwk[0])

def least_used_kit(_1:Namespace, coverage_data:dict, keebs:[dict], kits:[dict]) -> str:
    keeb_names:[str] = list(map(fst, keebs))
    keebs_with_non_disjoint_kits:List[str, List[Tuple[str, [dict]]]] = list(map(lambda p: (p[0], reduce(concat, map(lambda cs: list(map(fst, cs)), p[1]), [])), filter(lambda p: p[0] in keeb_names, coverage_data['compute_covering_set'].items())))

    occurrences:dict = { kit: [] for kit,_ in kits }
    for keeb,non_disjoint_kits in keebs_with_non_disjoint_kits:
        for kit in non_disjoint_kits:
            occurrences[kit] += [keeb]

    counted_occurrences:List[Tuple[str, int]] = list(map(lambda p: (p[0], len(p[1])), occurrences.items()))
    if counted_occurrences == []:
        return None
    luk:Tuple[str, int] = min(counted_occurrences, key=snd)

    return '%s (%d)' % luk
