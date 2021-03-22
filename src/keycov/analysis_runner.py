import keycov.analyses as analyses_mod
from .analyses import analyses, AnalysisFailedError, AnalysisTypes, DEFAULT_VERBOSITY, FailedAnalysisResult
from .args import Namespace
from .coverage_analyser import get_covering_sets
from .util import dict_union, fst, iconcat, snd
from functools import reduce
from sys import stderr
from types import SimpleNamespace
from typing import Callable, List, Set, Tuple, Union

def run_analyses(pargs:Namespace, keeb_layouts:[[dict]], kit_layouts:[[dict]], keys:[int], de_primer:dict) -> Tuple[int, List[dict]]:
    # Sanitise and linearise analyses
    sanitised_analyses:[dict] = sanitise_analyses(analyses)
    ordered_analyses:[dict] = linearise_analyses(sanitised_analyses)

    # Prepare data-structures
    exit_code:int = 0
    coverage_data:dict = {
        '~results': { 'de_primer': de_primer },
        'local-keeb-results': { l[0]:{} for l in keeb_layouts },
        'local-kit-results': { l[0]:{} for l in kit_layouts },
        'local-key-results': { k:{} for k in keys},
        'global-results': {}
    }

    # Prepare the arguments
    aargs:Namespace = SimpleNamespace(**pargs.__dict__, **{ 'de_primer': de_primer })

    # Run the analyses
    for analysis in ordered_analyses:
        if not hasattr(analyses_mod, analysis['func-name']):
            print('Analysis function "%s" was requested but is not present in module src.analyses' % analysis['func-name'], file=stderr)
            exit_code = -1
            continue
        func:Callable = getattr(analyses_mod, analysis['func-name'])
        props:int = analysis['analysis-properties']
        if props & AnalysisTypes.GLOBAL:
            ret:object
            try:
                ret = func(aargs, coverage_data['~results'], keeb_layouts, kit_layouts)
            except AnalysisFailedError as afe:
                print(afe.message, file=stderr)
                exit_code |= analysis['exit-code']
            if type(ret) == FailedAnalysisResult:
                exit_code |= analysis['exit-code']
                ret = ret.result
            if aargs.analysis_verbosity >= analysis['verbosity']:
                coverage_data['global-results'][analysis['pretty-name']] = ret
            coverage_data['~results'][analysis['func-name']] = ret
        elif props & AnalysisTypes.LOCAL:
            coverage_data['~results'][analysis['func-name']] = {}
            if props & AnalysisTypes.INDIVIDUAL_KITS or props & AnalysisTypes.INDIVIDUAL_KEEBS:
                if props & AnalysisTypes.INDIVIDUAL_KITS:
                    exit_code |= handle_analysis_on_individuals(aargs, analysis, func, coverage_data, 'local-kit-results', kit_layouts)
                if props & AnalysisTypes.INDIVIDUAL_KEEBS:
                    exit_code |= handle_analysis_on_individuals(aargs, analysis, func, coverage_data, 'local-keeb-results', keeb_layouts)
            elif props & AnalysisTypes.ITERATE_KITS or props & AnalysisTypes.ITERATE_KEEBS:
                if props & AnalysisTypes.ITERATE_KITS:
                    exit_code |= handle_analysis_iteration(aargs, analysis, func, coverage_data, 'local-kit-results', kit_layouts, keeb_layouts)
                if props & AnalysisTypes.ITERATE_KEEBS:
                    exit_code |= handle_analysis_iteration(aargs, analysis, func, coverage_data, 'local-keeb-results', keeb_layouts, kit_layouts)
            elif props & AnalysisTypes.ITERATE_KIT_KEYS or props & AnalysisTypes.ITERATE_KEEB_KEYS:
                if props & AnalysisTypes.ITERATE_KIT_KEYS:
                    exit_code |= handle_analysis_on_keys(aargs, analysis, func, coverage_data, 'local-key-results', keys, kit_layouts)
                if props & AnalysisTypes.ITERATE_KEEB_KEYS:
                    exit_code |= handle_analysis_on_keys(aargs, analysis, func, coverage_data, 'local-key-results', keys, keeb_layouts)

    sanitised_coverage_data:dict = sanitise(coverage_data)

    return (exit_code, sanitised_coverage_data)

def handle_analysis_on_individuals(aargs:Namespace, analysis:dict, func:Callable, coverage_data:dict, output_key:str, const_layouts:[[dict]], perform_analysis:bool=True) -> int:
    exit_code:int = 0
    for const_layout in const_layouts:
        ret:object = None
        if perform_analysis:
            try:
                ret = func(aargs, coverage_data['~results'], const_layout)
            except AnalysisFailedError as afe:
                print(afe.message, file=stderr)
                exit_code = analysis['exit-code']
            if type(ret) == FailedAnalysisResult:
                exit_code |= analysis['exit-code']
                ret = ret.result
        if aargs.analysis_verbosity >= analysis['verbosity']:
            coverage_data[output_key][const_layout[0]][analysis['pretty-name']] = ret
        coverage_data['~results'][analysis['func-name']][const_layout[0]] = ret
    return exit_code

def handle_analysis_iteration(aargs:Namespace, analysis:dict, func:Callable, coverage_data:dict, output_key:str, iter_layouts:[dict], const_layouts:[[dict]], perform_analysis:bool=True) -> int:
    exit_code:int = 0
    for iter_layout in iter_layouts:
        ret:object = None
        if perform_analysis:
            try:
                ret = func(aargs, coverage_data['~results'], iter_layout, const_layouts)
            except AnalysisFailedError as afe:
                print(afe.message, file=stderr)
                exit_code = analysis['exit-code']
            if type(ret) == FailedAnalysisResult:
                exit_code |= analysis['exit-code']
                ret = ret.result
        if aargs.analysis_verbosity >= analysis['verbosity']:
            coverage_data[output_key][iter_layout[0]][analysis['pretty-name']] = ret
        coverage_data['~results'][analysis['func-name']][iter_layout[0]] = ret
    return exit_code

def handle_analysis_on_keys(aargs:Namespace, analysis:dict, func:Callable, coverage_data:dict, output_key:str, keys:[dict], const_layouts:[[dict]], perform_analysis:bool = True) -> int:
    exit_code:int = 0
    for key in keys:
        ret:object = None
        if perform_analysis:
            try:
                ret = func(aargs, coverage_data['~results'], key, const_layouts)
            except AnalysisFailedError as afe:
                print(afe.message, file=stderr)
                exit_code = analysis['exit-code']
            if type(ret) == FailedAnalysisResult:
                exit_code |= analyis['exit-code']
                ret = ret.result
        if aargs.analysis_verbosity >= analysis['verbosity']:
            coverage_data[output_key][key][analysis['pretty-name']] = ret
        coverage_data['~results'][analysis['func-name']][key] = ret
    return exit_code

def sanitise(coverage_data:Union[dict, List[dict]]) -> dict:
    de_primer:dict = coverage_data['~results']['de_primer']

    # Remove local data if no analyses are to be printed
    local_result_keys:[str] = ['local-keeb-results', 'local-kit-results', 'local-key-results']
    for local_result_key in local_result_keys:
        if coverage_data[local_result_key] == {} or list(coverage_data[local_result_key].items())[0][1] == {}:
            coverage_data[local_result_key] = {}

    # Make the results table-friendly
    coverage_data['global-results'] = list(map(lambda p: { 'Analysis': p[0], 'Value': p[1] }, sorted(coverage_data['global-results'].items(), key=lambda p: p[0])))
    for local_result_key in local_result_keys:
        pretty_local_result_key:str
        pretty_key:Callable
        if local_result_key == 'local-key-results':
            pretty_local_result_key:str = 'Key'
            pretty_key = lambda rk: de_primer[rk]['pretty-name']
        else:
            pretty_local_result_key:str = 'Layout'
            pretty_key = lambda x: x
        coverage_data[local_result_key] = list(map(lambda p: dict_union({ pretty_local_result_key: pretty_key(p[0]) }, p[1]), coverage_data[local_result_key].items()))

    key_map:dict = {
        'global-results': 'General analysis',
        'local-keeb-results': 'Keyboard-specific analysis',
        'local-kit-results': 'Kit-specific analysis',
        'local-key-results': 'Key-specific results',
    }
    renamed_coverage_data:dict = dict(map(lambda p: (key_map[p[0]] if p[0] in key_map else p[0], p[1]), coverage_data.items()))

    return renamed_coverage_data

def sanitise_analyses(analyses:[dict]) -> [dict]:
    defaults:dict = {
        'verbosity': lambda _: DEFAULT_VERBOSITY,
        'analysis-properties': lambda _: AnalysisTypes.GLOBAL,
        'pretty-name': lambda a: a['name'],
        'exit-code': lambda _: 1,
        'func-name': lambda a: a['name'][1:] if a['name'].startswith('~') else a['name']
    }
    for analysis in analyses:
        for default in defaults:
            if default not in analysis:
                analysis[default] = defaults[default](analysis)
    return analyses

def linearise_analyses(analyses:[dict]) -> [dict]:
    # Compute required-by
    analyses.append({ 'name': 'SOURCE', 'requires': list(map(lambda a: a['name'], analyses)) })
    analyses_dict:dict = { a['name']: a for a in analyses }
    for aname in analyses_dict:
        analyses_dict[aname]['required-by'] = ['SOURCE']
    for aname in analyses_dict:
        if 'requires' in analyses_dict[aname]:
            for rname in analyses_dict[aname]['requires']:
                if rname not in analyses_dict:
                    print('Analysis "%s" has non-existent dependency "%s"' % (aname, rname), file=stderr)
                    exit(-1)
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
