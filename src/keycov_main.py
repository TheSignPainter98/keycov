from .args import Namespace, parse_args
from .coverage_data import compute_coverage_data
from .text_output import output_as_text as tdump
from .parse_kle import parse_kle
from .path import get_json_and_yaml_files
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
    input_layouts:[Tuple[str, List[dict]]] = list(map(parse_named_kle, input_layout_files))
    target_layouts:[Tuple[str, List[dict]]] = list(map(parse_named_kle, target_layout_files))

    # Analyse coverage
    coverage_data:[[dict]] = compute_coverage_data(target_layouts, input_layouts)

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
