import src.analyses as analyses_mod
from .analyses import analyses, AnalysisFailedError, AnalysisTypes, DEFAULT_VERBOSITY, FailedAnalysisResult
from .args import Namespace
from .coverage_analyser import get_covering_sets
from .util import dict_union, fst, iconcat, snd
from functools import reduce
from sys import stderr
from typing import Callable, List, Set, Tuple, Union

def run_analyses(pargs:Namespace, keeb_layouts:[[dict]], kit_layouts:[[dict]]) -> Tuple[int, List[dict]]:
    # Sanitise and linearise analyses
    sanitised_analyses:[dict] = sanitise_analyses(analyses)
    ordered_analyses:[dict] = linearise_analyses(sanitised_analyses)

    # Prepare data-structures
    exit_code:int = 0
    coverage_data:dict = { '~results': {}, 'local-keeb-results': { l[0]:{} for l in keeb_layouts }, 'local-kit-results': { l[0]:{} for l in kit_layouts }, 'global-results': {} }

    # Run the analyses
    for analysis in ordered_analyses:
        fname:str = analysis['name'] if not analysis['name'].startswith('~') else analysis['name'][1:]
        if not hasattr(analyses_mod, fname):
            print('Analysis function "%s" was requested but is not present in module src.analyses' % fname, file=stderr)
            exit_code = -1
            continue
        func:Callable = getattr(analyses_mod, fname)
        props:int = analysis['analysis-properties']
        if props & AnalysisTypes.GLOBAL:
            ret:object
            try:
                ret = func(pargs, coverage_data, keeb_layouts, kit_layouts)
            except AnalysisFailedError as afe:
                print(afe.message, file=stderr)
                exit_code |= analysis['exit-code']
            if type(ret) == FailedAnalysisResult:
                exit_code |= analysis['exit-code']
                ret = ret.result
            if pargs.analysis_verbosity >= analysis['verbosity']:
                coverage_data['global-results'][analysis['pretty-name']] = ret
            coverage_data['~results'][analysis['name']] = ret
        elif props & AnalysisTypes.LOCAL:
            coverage_data['~results'][analysis['name']] = {}
            if props & AnalysisTypes.INDIVIDUAL_KITS or props & AnalysisTypes.INDIVIDUAL_KEEBS:
                if props & AnalysisTypes.INDIVIDUAL_KITS:
                    exit_code |= handle_analysis_on_individuals(pargs, analysis, func, coverage_data, 'local-kit-results', kit_layouts)
                if props & AnalysisTypes.INDIVIDUAL_KEEBS:
                    exit_code |= handle_analysis_on_individuals(pargs, analysis, func, coverage_data, 'local-keeb-results', keeb_layouts)
            else:
                if props & AnalysisTypes.ITERATE_KITS:
                    exit_code |= handle_analysis_iteration(pargs, analysis, func, coverage_data, 'local-kit-results', kit_layouts, keeb_layouts)
                if props & AnalysisTypes.ITERATE_KEEBS:
                    exit_code |= handle_analysis_iteration(pargs, analysis, func, coverage_data, 'local-keeb-results', keeb_layouts, kit_layouts)

    sanitised_coverage_data:dict = sanitise(coverage_data)

    return (exit_code, sanitised_coverage_data)

def handle_analysis_on_individuals(pargs:Namespace, analysis:dict, func:Callable, coverage_data:dict, output_key:str, const_layouts:[[dict]], perform_analysis:bool=True) -> int:
    exit_code:int = 0
    for const_layout in const_layouts:
        ret:object = None
        if perform_analysis:
            try:
                ret = func(pargs, coverage_data, const_layout)
            except AnalysisFailedError as afe:
                print(afe.message, file=stderr)
                exit_code = analysis['exit-code']
            if type(ret) == FailedAnalysisResult:
                exit_code |= analysis['exit-code']
                ret = ret.result
        if pargs.analysis_verbosity >= analysis['verbosity']:
            coverage_data[output_key][const_layout[0]][analysis['pretty-name']] = ret
        coverage_data['~results'][analysis['name']][const_layout[0]] = ret
    return exit_code

def handle_analysis_iteration(pargs:Namespace, analysis:dict, func:Callable, coverage_data:dict, output_key:str, iter_layouts:[dict], const_layouts:[[dict]], perform_analysis:bool=True) -> int:
    exit_code:int = 0
    for iter_layout in iter_layouts:
        ret:object = None
        if perform_analysis:
            try:
                ret = func(pargs, coverage_data, iter_layout, const_layouts)
            except AnalysisFailedError as afe:
                print(afe.message, file=stderr)
                exit_code = analysis['exit-code']
            if type(ret) == FailedAnalysisResult:
                exit_code |= analysis['exit-code']
                ret = ret.result
        if pargs.analysis_verbosity >= analysis['verbosity']:
            coverage_data[output_key][iter_layout[0]][analysis['pretty-name']] = ret
        coverage_data['~results'][analysis['name']][iter_layout[0]] = ret
    return exit_code

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

    # Remove local data if no analyses are to be printed
    local_result_keys:[str] = ['local-keeb-results', 'local-kit-results']
    for local_result_key in local_result_keys:
        if list(coverage_data[local_result_key].items())[0][1] == {}:
            coverage_data[local_result_key] = {}

    # Make the results table-friendly
    coverage_data['global-results'] = list(map(lambda p: { 'Analysis': p[0], 'Value': p[1] }, sorted(coverage_data['global-results'].items(), key=lambda p: p[0])))
    for local_result_key in local_result_keys:
        coverage_data[local_result_key] = list(map(lambda p: dict_union({ 'Layout': p[0] }, p[1]), coverage_data[local_result_key].items()))

    key_map:dict = {
        'global-results': 'General analysis',
        'local-keeb-results': 'Keyboard-specific analysis',
        'local-kit-results': 'Kit-specific analysis',
    }
    renamed_coverage_data:dict = dict(map(lambda p: (key_map[p[0]], p[1]), coverage_data.items()))

    return renamed_coverage_data

def sanitise_analyses(analyses:[dict]) -> [dict]:
    defaults:dict = {
        'verbosity': lambda _: DEFAULT_VERBOSITY,
        'analysis-properties': lambda _: AnalysisTypes.GLOBAL,
        'pretty-name': lambda a: a['name'],
        'exit-code': lambda _: 1,
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
