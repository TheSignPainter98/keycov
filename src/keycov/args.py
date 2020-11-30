# Copyright (C) Edward Jones

from .analyses import analyses, DEFAULT_VERBOSITY
from .util import default_terminal_dims, dict_union, dict_union_ignore_none, repeat, restrict_dict
from .version import version_notice
from argparse import ArgumentParser, Namespace
from beautifultable import ALIGN_LEFT, BeautifulTable
from functools import reduce
from os import getcwd, linesep
from os.path import dirname, join, normpath, relpath, sep
from shutil import get_terminal_size
from sys import exit, stderr
from typing import Callable

description:str = 'A little script for helping keycap designers analyse kitting coverage'

dir_str:Callable = lambda s: normpath(s) + sep
rel_path:Callable = lambda p: relpath(join(dirname(__file__), '..', p), start=getcwd())

args:[dict] = [
    {
        'dest': 'show_version',
        'short': '-V',
        'long': '--version',
        'action': 'store_true',
        'help': 'Show the current version and licensing information then exit',
        'type': bool,
        'default': False
    },
    {
        'dest': 'show_help',
        'short': '-h',
        'long': '--help',
        'action': 'store_true',
        'help': 'Show short help message and exit',
        'type': bool,
        'default': False
    },
    {
        'dest': 'show_long_help',
        'short': '-H',
        'long': '--long-help',
        'action': 'store_true',
        'type': bool,
        'default': False,
        'help': 'Show the longer help message and exit'
    },
    {
        'dest': 'input_dir',
        'short': '-k',
        'long': '--kit-dir',
        'action': 'store',
        'help': 'Specify the directory from which kit KLE files are read',
        'type': str,
        'sanitiser': dir_str,
        'metavar': 'dir',
        'default': rel_path('kits')
    },
    {
        'dest': 'target_dir',
        'short': '-l',
        'long': '--layout-dir',
        'action': 'store',
        'help': 'Specify the directory from which keyboard layouts KLEs to cover are read',
        'type': str,
        'sanitiser': dir_str,
        'metavar': 'dir',
        'default': rel_path('keebs')
    },
    {
        'dest': 'output_format',
        'short': '-f',
        'long': '--output-format',
        'action': 'store',
        'help': 'Specify the format of the outputted report',
        'type': str,
        'metavar': 'format',
        'default': 'text',
        'choices': [
            'json',
            'none',
            'text',
            'yaml',
        ]
    },
    {
        'dest': 'output_list_cutoff',
        'short': '-L',
        'long': '--list-cutoff',
        'action': 'store',
        'help': 'Limit the number of elements in list fields',
        'type': int,
        'metavar': 'num',
        'default': 5
    },
    {
        'dest': 'analysis_verbosity',
        'short': '-v',
        'long': '--analysis-verbosity',
        'metavar': 'level',
        'action': 'store',
        'help': 'Set the verbosity of analyses performed outputted',
        'type': int,
        'matavar': 'level',
        'default': 1,
        'choices': [
            0,
            1,
            2,
            3,
        ]
    },
    {
        'dest': 'force_colour',
        'short': '-C',
        'long': '--colour',
        'action': 'store_true',
        'help': 'Force colour output (override heuristics)',
        'type': bool,
        'default': False
    },
    {
        'dest': 'force_no_colour',
        'short': '-c',
        'long': '--no-colour',
        'action': 'store_true',
        'help': 'Force no colour output (override heuristics)',
        'type': bool,
        'default': False
    },
    {
        'dest': 'theme',
        'short': '-t',
        'long': '--theme',
        'action': 'store',
        'metavar': 'theme',
        'help': 'Set the colour theme for the text-output tables',
        'type': str,
        'default': rel_path('themes/default.yml')
    }
]
arg_dict:dict = { a['dest']: a for a in args if 'dest' in a }

##
# @brief Parse commandline arguments
# If an error occurs, the an exception is raised
#
# @param args:[str] A list of commandline arguments, including argv[0], the program name
#
# @return A namespace of options
def parse_args(iargs: tuple) -> Namespace:
    ap: ArgumentParser = ArgumentParser(description=description, add_help=False)

    # Generate the argument parser
    for arg in list(sorted(args, key=lambda arg: arg['short'].lower())):
        ap.add_argument(
            arg['short'], arg['long'],
            **dict_union(
                {
                    k: v
                    for k, v in arg.items()
                    if k in ['dest', 'action', 'metavar', 'version'] + (['type'] if arg['type'] != bool else [])
                },
                {'help': arg['help'] + arg_inf(arg)} if 'help' in arg else {}))

    # Sanitise and obtain parsed arguments
    pargs: dict = ap.parse_args(iargs[1:]).__dict__

    dargs = { a['dest']: a['default'] for a in args if 'dest' in a }
    rargs: dict = dict_union_ignore_none(dargs, pargs)
    #  rargs = dict(map(lambda p: (p[0], arg_dict[p[0]]['type'](p[1])), rargs.items()))
    checkResult:str = check_args(rargs)
    if checkResult is not None:
        ap.print_usage()
        print(checkResult, file=stderr)
        exit(-1)

    # Sanitise arguments
    for arg in args:
        if 'sanitiser' in arg:
            rargs[arg['dest']] = arg['sanitiser'](rargs[arg['dest']])

    npargs:Namespace = Namespace(**rargs)
    if npargs.show_help:
        ap.print_help()
        exit(0)
    elif npargs.show_long_help:
        ap.print_help()
        print(get_long_help())
        exit(0)
    elif npargs.show_version:
        print(version_notice)
        exit(0)


    return npargs

def check_args(args: dict) -> 'Maybe str':
    items: [[str, object]] = args.items()
    if all(map(lambda a: type(a[1]) == arg_dict[a[0]]['type'], items)) and all(map( lambda a: 'choices' not in arg_dict[a[0]] or a[1] in arg_dict[a[0]] ['choices'], items)):
        return None
    wrong_types:[str] = list(map(lambda a: 'Expected %s value for %s but got %s' %(str(arg_dict[a[0]]['type']), arg_dict[a[0]]['dest'], str(a[1])), filter(lambda a: type(a[1]) != arg_dict[a[0]]['type'], items)))
    wrong_choices:[str] = list(map(lambda a: 'Argument %s only accepts %s but got %s' % (arg_dict[a[0]]['dest'], ', '.join(list(map(str, arg_dict[a[0]]['choices']))), str(a[1])), filter(lambda a: 'choices' in arg_dict[a[0]] and a[1] not in arg_dict[a[0]]['choices'], items)))

    return '\n'.join(wrong_types + wrong_choices)

def arg_inf(arg:dict) -> str:
    info:[str] = []
    arg_formats:[Tuple[str,Callable]] = [
        ('default', lambda s: 'default: %s' % s),
        ('choices', lambda s: 'choices: { %s }' % ', '.join(map(str,s))),
        ('arg_inf_msg', str),
    ]
    for k,f in arg_formats:
        if k in arg:
            info.append(f(arg[k]))

    info_str:str = ''
    if info != []:
        info_str = ' (%s)' % ', '.join(info)
    else:
        info_str = ''
    return info_str

def get_long_help() -> str:
    table:BeautifulTable = BeautifulTable()
    #  Add the data
    for r in list(map(lambda a: [a['pretty-name'], a['description'] + ' (verbosity-level: %d)' %(a['verbosity'] if 'verbosity' in a else DEFAULT_VERBOSITY)], filter(lambda a: 'pretty-name' in a and not a['name'].startswith('~'), analyses))):
        table.rows.append(r)

    # Apply styling
    table.columns.alignment = ALIGN_LEFT
    table.rows.alignment = ALIGN_LEFT
    table.border.top = ''
    table.border.right = ''
    table.border.bottom = ''
    table.border.left = ''
    table.columns.header.separator = '─'
    table.columns.separator = ''
    table.rows.separator = ''
    table.maxwidth = get_terminal_size(default_terminal_dims).columns
    table.detect_numerics = False


    return linesep + 'analyses to be performed:' + linesep + str(table)