from .util import add, fst, snd
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

analyses:[dict] = [
    {
        'name': 'num_keebs',
        'pretty-name': 'Layouts analysed',
        'description': 'Total number of keyboard layouts analysed',
    },
    {
        'name': 'num_kits',
        'pretty-name': 'Kits analysed',
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
        'pretty-name': 'Most common keys in keyboard layouts',
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
        'name': '~covering_set_of_lowest_units',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~compute_covering_set'
        ]
    },
    {
        'name': 'covering_set_of_lowest_units_surplus',
        'verbosity': 2,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_units'
        ]
    },
    {
        'name': 'covering_set_of_lowest_units_value',
        'verbosity': 3,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_units'
        ]
    },
    {
        'name': '~covering_set_of_lowest_cardinality',
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~compute_covering_set'
        ]
    },
    {
        'name': 'covering_set_of_lowest_cardinality_amount',
        'verbosity': 2,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_cardinality'
        ]
    },
    {
        'name': 'covering_set_of_lowest_cardinality_value',
        'verbosity': 3,
        'analysis-properties': AnalysisTypes.LOCAL | AnalysisTypes.INDIVIDUAL_KEEBS,
        'requires': [
            '~covering_set_of_lowest_cardinality'
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
    sorted_occurrences:[str] = list(map(lambda p: '%s (%s)' %(p[0], p[1]), sorted(key_occurrences.items(), key=snd, reverse=True)))

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
    return get_covering_sets(keeb, kits)

def exists_covering_set(_1:dict, coverage_data:dict, layout:[dict]) -> bool:
    return coverage_data['~results']['~compute_covering_set'][layout[0]] != []

def number_of_covering_sets(_1:dict, coverage_data:dict, layout:[dict]) -> int:
    covering_sets:list = coverage_data['~results']['~compute_covering_set'][layout[0]]
    return len(covering_sets)

def covering_set_of_lowest_units(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> Tuple[str, List[dict]]:
    css:List[Tuple[str, List[dict]]] = coverage_data['~results']['~compute_covering_set'][keeb[0]]
    return min(map(lambda cs: (reduce(add, map(lambda s: get_total_units(s), cs), 0.0), cs), css), key=fst)

def covering_set_of_lowest_units_surplus(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> float:
    cs:Tuple[float, List[Tuple[str, List[dict]]]] = coverage_data['~results']['~covering_set_of_lowest_units'][keeb[0]]
    return cs[0] - get_total_units(keeb)

def covering_set_of_lowest_units_value(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> [str]:
    return list(map(fst, coverage_data['~results']['~covering_set_of_lowest_units'][keeb[0]][1]))

def covering_set_of_lowest_cardinality(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> float:
    css:List[Tuple[str, List[dict]]] = coverage_data['~results']['~compute_covering_set'][keeb[0]]
    return min(map(lambda cs: (len(cs), cs), css), key=fst)

def covering_set_of_lowest_cardinality_amount(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> float:
    cs:Tuple[float, List[Tuple[str, List[dict]]]] = coverage_data['~results']['~covering_set_of_lowest_cardinality'][keeb[0]]
    return cs[0]

def covering_set_of_lowest_cardinality_value(_1:Namespace, coverage_data:dict, keeb:Tuple[str, List[dict]]) -> [str]:
    return list(map(fst, coverage_data['~results']['~covering_set_of_lowest_cardinality'][keeb[0]][1]))
