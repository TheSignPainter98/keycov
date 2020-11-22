from .util import iconcat
from functools import reduce
from typing import List, Tuple

analyses:[dict] = [
    {
        'name': 'asdf',
        'pretty-name': 'ASDF',
        'description': 'Test thingy',
        'operation': lambda _: {},
        'requires': [
            'fdsa'
        ]
    },
    {
        'name': 'fdsa',
        'pretty-name': 'FDJHSAKLFH',
        'description': 'Asdf',
        'operation': lambda _: {},
        'requires': [ 'preqw' ]
    },
    {
        'name': 'preqw',
        'pretty-name': 'hklqwe',
        'description': 'fdafdsaf'
    }
]

def compute_coverage_data(target_layouts:[[dict]], input_layouts:[[dict]]) -> [[dict]]:
    ordered_analyses:[dict] = linearise_analyses(analyses)
    print(ordered_analyses)

    coverage_data:[dict] = [list(map(lambda p: { 'target': p[0], 'num-r4s': len(list(filter(lambda k: k['p'] == 'R4', p[1]))) }, target_layouts))]
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

    return linearised_analyses
