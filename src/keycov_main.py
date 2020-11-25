from .args import Namespace, parse_args
from .text_output import output_as_text
from .analysis_runner import run_analyses
from .parse_kle import parse_kle
from .path import get_json_and_yaml_files
from .util import key_pretty_name, serialise_key
from json import dumps as jdump
from os import linesep
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
    exit_code:int
    coverage_data:List[dict]
    (exit_code, coverage_data) = run_analyses(pargs, target_layouts, input_layouts)

    # Output coverage data
    tdump:Callable = lambda cd: output_as_text(pargs, cd)
    output_formatter:dict = {
        'text': tdump,
        'json': jdump,
        'yaml': ydump,
        'none': lambda _: '',
    }
    coverage_report:str = output_formatter[pargs.output_format](coverage_data)
    print(coverage_report, end='')
    if not coverage_report.endswith(linesep) and coverage_report:
        print()

    return exit_code

def parse_named_kle(fname:str) -> Tuple[str, List[dict]]:
    return (fname, parse_kle(fname))

def sanitise_layouts(target_layouts:[dict], input_layouts:[dict]):
    for layout in target_layouts + input_layouts:
        for key in layout[1]:
            key['serialised'] = serialise_key(key)
            key['pretty-name'] = key_pretty_name(key)
