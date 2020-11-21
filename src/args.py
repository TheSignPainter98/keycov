# Copyright (C) Edward Jones

from argparse import ArgumentParser, Namespace
from functools import reduce
from sys import exit, stderr

description:str = 'A little script for helping keycap designers analyse kitting coverage'

args:[dict] = [
    {
        'dest': 'show_help',
        'short': '-h',
        'long': '--help',
        'action': 'help',
        'help': 'Show this help message and exit',
        'type': bool,
        'default': False
    },
    {
        'dest': 'input_dir',
        'short': '-k',
        'long': '--kit-dir',
        'action': 'store',
        'help': 'Specify the directory from which kit kle files are read',
        'type': str,
        'metavar': 'dir',
        'default': 'kits'
    },
    {
        'dest': 'target_dir',
        'short': '-l',
        'long': '--layout-dir',
        'action': 'store',
        'help': 'Specify the directory from which layouts to cover files are read',
        'type': str,
        'metavar': 'dir',
        'default': 'keebs'
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
            'text',
            'yaml',
            'json'
        ]
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
        exit(1)

    npargs:Namespace = Namespace(**rargs)
    if npargs.show_help:
        ap.print_help()
        raise AdjustKeysGracefulExit()

    return npargs


def check_args(args: dict) -> 'Maybe str':
    items: [[str, object]] = args.items()
    if all(map(lambda a: type(a[1]) == arg_dict[a[0]]['type'], items)) and all(map( lambda a: 'choices' not in arg_dict[a[0]] or a[1] in arg_dict[a[0]] ['choices'], items)):
        return None
    wrong_types:[str] = list(map(lambda a: 'Expected %s value for %s but got %s' %(str(arg_dict[a[0]]['type']), arg_dict[a[0]]['dest'], str(a[1])), filter(lambda a: type(a[1]) != arg_dict[a[0]]['type'], items)))
    wrong_choices:[str] = list(map(lambda a: 'Argument %s only accepts %s but got %s' % (arg_dict[a[0]]['dest'], ', '.join(list(map(str, arg_dict[a[0]]['choices']))), str(a[1])), filter(lambda a: 'choices' in arg_dict[a[0]] and a[1] not in arg_dict[a[0]]['choices'], items)))

    return '\n'.join(wrong_types + wrong_choices)

def arg_inf(arg:dict) -> str:
    if 'default' in arg:
        return ' (default: %s%s)' % (arg['default'], ' ' + arg['arg_inf_msg'] if 'arg_inf_msg' in arg else '')
    return ''

def dict_union_ignore_none(a: dict, b: dict) -> dict:
    return dict(a, **dict(filter(lambda p: p[1] is not None, b.items())))

def dict_union(*ds:[dict]) -> dict:
    def _dict_union(a:dict, b:dict) -> dict:
        return dict(a, **b)
    return dict(reduce(_dict_union, ds, {}))
