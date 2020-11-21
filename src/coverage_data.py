from .util import iconcat
from functools import reduce
from typing import List, Tuple

def compute_coverage_data(target_layouts:Tuple[str, List[dict]], input_layouts:Tuple[str, List[dict]]) -> [dict]:
    coverage_data:[dict] = list(map(lambda p: { 'target': p[0], 'num-r4s': len(list(filter(lambda k: k['p'] == 'R4', p[1]))) }, target_layouts))

    return coverage_data
