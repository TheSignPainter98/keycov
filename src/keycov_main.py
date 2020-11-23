from .args import Namespace, parse_args
from .coverage_analyser import analyse_coverage
from .text_output import output_as_text as tdump
from .parse_kle import parse_kle
from .path import get_json_and_yaml_files
from .util import serialise_key
from json import dumps as jdump
from os import linesep
from texttable import Texttable
from typing import List, Tuple
from yaml import dump as ydump

def main(args:[str]) -> int:
    # Parse arguments
    pargs:Namespace = parse_args(args)

    # Collect input data
    input_layout_files:[str] = get_json_and_yaml_files(pargs.input_dir)
    target_layout_files:[str] = get_json_and_yaml_files(pargs.target_dir)
    input_layouts:[[dict]] = list(map(parse_named_kle, input_layout_files))
    target_layouts:[[dict]] = list(map(parse_named_kle, target_layout_files))

    # Prepare data
    sanitise_layouts(target_layouts, input_layouts)

    # Analyse coverage
    coverage_data:[[dict]] = analyse_coverage(target_layouts, input_layouts)

    # Output coverage data
    output_formatter:dict = {
        'text': tdump,
        'json': jdump,
        'yaml': ydump,
    }
    coverage_report:str = output_formatter[pargs.output_format](coverage_data)
    print(coverage_report, end='')
    if not coverage_report.endswith(linesep):
        print()

    return 0

def parse_named_kle(fname:str) -> Tuple[str, List[dict]]:
    return (fname, parse_kle(fname))

def sanitise_layouts(target_layouts:[dict], input_layouts:[dict]):
    for target_layout in target_layouts:
        for key in target_layout[1]:
            key['serialised'] = serialise_key(key)
    for input_layout in input_layouts:
        for key in input_layout[1]:
            key['serialised'] = serialise_key(key)
