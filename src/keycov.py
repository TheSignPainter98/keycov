#!/usr/bin/env python3

from json import dumps as jdump
from keycov.analysis_runner import run_analyses
from keycov.args import args, Namespace, parse_args
from keycov.parse_kle import parse_kle
from keycov.path import get_json_and_yaml_files
from keycov.text_output import output_as_text
from keycov.util import dict_union, key_pretty_name, serialise_key, snd
from math import ceil, sqrt
from os import linesep
from sys import argv, exit
from typing import List, Tuple, Union
from yaml import dump as ydump

def main(args:[str]) -> int:
    # Parse arguments
    pargs:Namespace = parse_args(args)

    # Perform the analysis
    exit_code:int
    coverage_data:List[dict]
    de_primer:dict
    known_paths:[str]
    (exit_code, coverage_data, known_paths) = keycov(pargs)

    # Output coverage data
    tdump:Callable = lambda cd: output_as_text(pargs, known_paths, cd)
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

def keycov(pargs:Union[Namespace, dict]) -> Tuple[int, dict, List[str]]:
    # Apply default arguments if (possibly-incomplete) dictionary passed
    if type(pargs) == dict:
        dargs = dict(map(lambda d: (d['dest'], d['default']), args))
        pargs = Namespace(**dict_union(dargs, pargs))

    # Collect input data
    input_layout_files:[str] = get_json_and_yaml_files(pargs.input_dir)
    target_layout_files:[str] = get_json_and_yaml_files(pargs.targets)
    input_layouts:[[dict]] = list(map(parse_named_kle, input_layout_files))
    target_layouts:[[dict]] = list(map(parse_named_kle, target_layout_files))
    known_paths:[str] = input_layout_files + target_layout_files

    # Prepare data
    sanitise_layouts(target_layouts + input_layouts)
    keys:[dict]
    de_primer:dict
    (de_primer, keys) = prepare_keys(input_layouts + target_layouts)

    # Analyse coverage
    exit_code:int
    coverage_data:List[dict]
    (exit_code, coverage_data) = run_analyses(pargs, target_layouts, input_layouts, keys, de_primer)
    coverage_data['~results']['de_primer'] = de_primer
    return (exit_code, coverage_data, known_paths)

def parse_named_kle(fname:str) -> Tuple[str, List[dict]]:
    return (fname, parse_kle(fname))

def sanitise_layouts(layouts:[dict]):
    for layout in layouts:
        for key in layout[1]:
            key['serialised'] = serialise_key(key)
            key['pretty-name'] = key_pretty_name(key)

def prepare_keys(layouts:[tuple]) -> Tuple[dict, List[dict]]:
    prime:iter = primes()
    seen_keys:dict = {}
    de_primer:dict = {}
    for layout in map(snd, layouts):
        for ki in range(len(layout)):
            key:dict = layout[ki]
            if key['serialised'] not in seen_keys:
                p:int = next(prime)
                seen_keys[key['serialised']] = p
                de_primer[p] = key
            layout[ki] = seen_keys[key['serialised']]

    return (de_primer, list(de_primer.keys()))

def primes() -> [int]:
    i:int = 3
    while True:
        yield i
        while True:
            i += 2
            if is_prime(i):
                break

def is_prime(n:int) -> bool:
    # Assume n >= 3
    for i in range(2, ceil(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == '__main__':
    exit(main(argv))
