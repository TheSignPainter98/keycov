from .util import dict_union, fst, iconcat, snd
from functools import reduce
from typing import Callable, List, Tuple, Union

LOCAL:int = 0x1
GLOBAL:int = 0x2
INDIVIDUAL_INPUTS:int = 0x4
INDIVIDUAL_TARGETS:int = 0x8
ITERATE_INPUTS:int = 0x10
ITERATE_TARGETS:int = 0x20

analyses:[dict] = [
    {
        'name': 'num_keebs',
        'pretty-name': 'Layouts analysed',
        'description': 'Total number of keyboard layouts analysed',
        'analysis-properties': GLOBAL
    },
    {
        'name': 'num_kits',
        'pretty-name': 'Kits analysed',
        'description': 'Total number of kits analysed',
        'analysis-properties': GLOBAL
    },
    {
        'name': 'most_common_kit_keys',
        'pretty-name': 'Most common keys in kits',
        'description': 'Finds out the 10 keys which are the most common in the kits presented',
        'analysis-properties': GLOBAL,
        'output-cutoff': 5
    },
    {
        'name': 'most_common_keeb_keys',
        'pretty-name': 'Most common keys in keyboard layouts',
        'description': 'Finds out the 10 keys which are the most common in the target keyboard layouts presented',
        'analysis-properties': GLOBAL,
        'output-cutoff': 5
    },
    {
        'name': 'count_units',
        'pretty-name': 'Total units',
        'description': 'Computes the total number of units present in a given layout',
        'analysis-properties': LOCAL | INDIVIDUAL_INPUTS | INDIVIDUAL_TARGETS
    },
    {
        'name': '~covering_set',
        'analysis-properties': LOCAL | ITERATE_INPUTS | ITERATE_TARGETS
    },
    {
        'name': 'has_covering_set',
        'pretty-name': 'Is covered',
        'description': 'Describes for a keeb whether there exists a covering set of kits, or vice versa',
        'analysis-properties': LOCAL | INDIVIDUAL_INPUTS | INDIVIDUAL_TARGETS,
        'requires': [
            '~covering_set'
        ]
    },
    {
        'name': 'cardinality_of_covering_set',
        'pretty-name': 'Covering set size',
        'description': 'The number of kits required to cover a keyboard with the fewest surplus units, or vice versa',
        'analysis-properties': LOCAL | INDIVIDUAL_TARGETS,
        'requires': [
            '~covering_set'
        ]
    },
    {
        'name': 'surplus_covering_units',
        'pretty-name': 'Surplus covering units',
        'description': 'The number of extra units required to cover a keyboard with the available kits, or vice versa ',
        'analysis-properties': LOCAL | INDIVIDUAL_TARGETS,
        'requires': [
            '~covering_set',
            'count_units'
        ]
    },
]

def analyse_coverage(target_layouts:[[dict]], input_layouts:[[dict]]) -> [[dict]]:
    ordered_analyses:[dict] = linearise_analyses(analyses)

    all_layouts:[[dict]] = input_layouts + target_layouts
    coverage_data:dict = { '~results': {}, 'local-results': { l[0]:{} for l in all_layouts}, 'global-results': {} }
    for analysis in ordered_analyses:
        func:Callable = globals()[analysis['name'] if not analysis['name'].startswith('~') else analysis['name'][1:]]
        props:int = analysis['analysis-properties']
        if props & GLOBAL:
            ret:object = func(analysis, coverage_data, target_layouts, input_layouts)
            coverage_data['~results'][analysis['name']] = ret
            coverage_data['global-results'][analysis['pretty-name']] = ret
        elif props & LOCAL:
            coverage_data['~results'][analysis['name']] = {}
            if props & INDIVIDUAL_INPUTS or props & INDIVIDUAL_TARGETS:
                handle_analysis_on_individuals(analysis, func, coverage_data, props & INDIVIDUAL_INPUTS, input_layouts)
                handle_analysis_on_individuals(analysis, func, coverage_data, props & INDIVIDUAL_TARGETS, target_layouts)
            else:
                handle_analysis_iteration(analysis, func, coverage_data, props & ITERATE_INPUTS, input_layouts, target_layouts)
                handle_analysis_iteration(analysis, func, coverage_data, props & ITERATE_TARGETS, target_layouts, input_layouts)

    sanitised_coverage_data:dict = sanitise(coverage_data)

    return sanitised_coverage_data

def handle_analysis_on_individuals(analysis:dict, func:Callable, coverage_data:dict, perform_analysis:bool, const_layouts:[[dict]]):
    for const_layout in const_layouts:
        ret:object = None
        if perform_analysis:
            ret = func(analysis, coverage_data, const_layout)
        coverage_data['local-results'][const_layout[0]][analysis['pretty-name']] = ret
        coverage_data['~results'][analysis['name']][const_layout[0]] = ret

def handle_analysis_iteration(analysis:dict, func:Callable, coverage_data:dict, perform_analysis:bool, iter_layouts:[dict], const_layouts:[[dict]]):
    for iter_layout in iter_layouts:
        ret:object = None
        if perform_analysis:
            ret = func(analysis, coverage_data, iter_layout, const_layouts)
        if 'pretty-name' in analysis:
            coverage_data['local-results'][iter_layout[0]][analysis['pretty-name']] = ret
        coverage_data['~results'][analysis['name']][iter_layout[0]] = ret

def num_keebs(analysis:dict, coverage_data:dict, target_layouts:[dict], input_layouts:[dict]) -> int:
    return len(target_layouts)

def num_kits(analysis:dict, coverage_data:dict, target_layouts:[dict], input_layouts:[dict]) -> int:
    return len(input_layouts)

def most_common_kit_keys(analysis:dict, coverage_data:dict, target_layouts:[dict], input_layouts:[dict]) -> [str]:
    return most_common_keys(target_layouts, output_cutoff=analysis['output-cutoff'])

def most_common_keeb_keys(analysis:dict, coverage_data:dict, target_layouts:[dict], input_layouts:[dict]) -> [str]:
    return most_common_keys(input_layouts, output_cutoff=analysis['output-cutoff'])

def most_common_keys(layouts:[dict], output_cutoff:int=0) -> [str]:
    key_occurrences:dict = count_key_occurrences(layouts)
    sorted_occurrences:[str] = list(map(lambda p: '%s (%s)' %(p[0], p[1]), sorted(key_occurrences.items(), key=snd, reverse=True)))

    if output_cutoff > 0:
        return sorted_occurrences[:output_cutoff]
    return sorted_occurrences

def count_key_occurrences(layouts:Tuple[str, List[dict]]) -> dict:
    occurrences:dict = {}
    for layout in layouts:
        for key in layout[1]:
            if key['serialised'] in occurrences:
                occurrences[key['serialised']] += 1
            else:
                occurrences[key['serialised']] = 1
    return occurrences

def count_units(_1:dict, _2:dict, layout:tuple) -> float:
    return reduce(lambda a,b: a + b, map(get_units, layout[1]), 0.0)

def get_units(key:dict) -> float:
    considered_dims:[float] = [key['w'], key['h']]
    extra_dims:[float] = [key['w2'], key['h2']]
    if any(map(lambda v: v != 1, extra_dims)):
        considered_dims += extra_dims
    return max(considered_dims)

def covering_set(_1:dict, _2:dict, layout:[dict], layout_sets:[[dict]]) -> [tuple]:
    return [('asdf', [{ 'key': 'Q', 'w': 20.0, 'h': 22.0, 'w2': 1.0, 'h2': 1.0 }])]

def has_covering_set(_1:dict, coverage_data:dict, layout:[dict]) -> bool:
    return coverage_data['~results']['~covering_set'][layout[0]] is not None

def cardinality_of_covering_set(_1:dict, coverage_data:dict, layout:[dict]) -> int:
    covering_set:list = coverage_data['~results']['~covering_set'][layout[0]]
    return len(covering_set) if covering_set is not None else None

def surplus_covering_units(analysis:dict, coverage_data:dict, layout:[dict]) -> float:
    return reduce(lambda a,b: a + b, map(lambda l: count_units(analysis, coverage_data, l), coverage_data['~results']['~covering_set'][layout[0]]), 0.0) - coverage_data['~results']['count_units'][layout[0]]

def sanitise(coverage_data:Union[dict, List[dict]]) -> dict:
    def remove_private_data(cdata:Union[dict, List[dict]]) -> dict:
        if type(cdata) == dict:
            keys_to_remove:[str] = []
            for key in cdata:
                if type(key) == str and key.startswith('~'):
                    keys_to_remove.append(key)
            for rkey in keys_to_remove:
                del cdata[rkey]
            for key in cdata:
                cdata[key] = remove_private_data(cdata[key])
        elif type(cdata) in [list, tuple]:
            cdata = list(map(remove_private_data, cdata))
        return cdata

    remove_private_data(coverage_data)

    # Make the results table-friendly
    coverage_data['global-results'] = list(map(lambda p: { 'Analysis': p[0], 'Value': p[1] }, sorted(coverage_data['global-results'].items(), key=lambda p: p[0])))
    coverage_data['local-results'] = list(map(lambda p: dict_union({ 'Layout': p[0] }, p[1]), coverage_data['local-results'].items()))

    return coverage_data

def linearise_analyses(analyses:[dict]) -> [dict]:
    # Compute required-by
    analyses.append({ 'name': 'SOURCE', 'requires': list(map(lambda a: a['name'], analyses)) })
    analyses_dict:dict = { a['name']: a for a in analyses }
    for aname in analyses_dict:
        analyses_dict[aname]['required-by'] = ['SOURCE']
    for aname in analyses_dict:
        if 'requires' in analyses_dict[aname]:
            for rname in analyses_dict[aname]['requires']:
                analyses_dict[rname]['required-by'].append(aname)

    # Linearise along prerequisites (with a DFS)
    seen:set = { 'SOURCE' }
    linearised_analyses:[dict] = []
    def _linearise_analyses(aname:str) -> [dict]:
        nonlocal seen
        nonlocal linearised_analyses
        if 'requires' in analyses_dict[aname]:
            for rname in analyses_dict[aname]['requires']:
                if rname in seen or any(map(lambda r: r not in seen, analyses_dict[aname]['required-by'])):
                    continue
                seen.add(rname)
                _linearise_analyses(rname)
                linearised_analyses.append(rname)
    _linearise_analyses('SOURCE')

    return map(lambda l: analyses_dict[l], linearised_analyses)
