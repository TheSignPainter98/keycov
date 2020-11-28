from .args import Namespace
from .util import default_terminal_dims, dict_union, fst, special_properties
from .yaml_io import read_yaml
from beautifultable import ALIGN_LEFT, BeautifulTable
from os import environ, linesep
from os.path import sep
from re import match
from shutil import get_terminal_size
from sys import platform, stdout
from types import SimpleNamespace
from typing import List, Union

terminal_formats:dict = {}
formats:SimpleNamespace = None
default_formats:dict = {
    'tick_format': 0,
    'cross_format': 0,
    'num_format': 0,
    'header_format': 0,
    'path_format': 0,
    'empty_string_format': 0,
    'empty_string_string': '/',
    'empty_list_format': 0,
    'empty_list_string': '∅',
    'none_format': 0,
    'none_string': '-',
}
float_output_precision:int = 2
END_CODE:int = '\033[0m'

keycap_pretty_name_regex:str = r'^[^ \n]*[0-9]+\.[0-9]{2}x[0-9]+\.[0-9]{2}(\[[0-9]+\.[0-9]{2}x[0-9]+\.[0-9]{2}\])?(-[%s]+)?$' % ''.join(special_properties.keys())

def output_as_text(pargs:Namespace, known_paths:[str], coverage_data:dict) -> str:
    global formats, terminal_formats

    # Resolve the theme
    theme:dict = read_yaml(pargs.theme)
    terminal_formats = theme['terminal_formats']
    formats = SimpleNamespace(**dict_union(default_formats, theme['formats']))

    # Remove data not to be printed
    remove_private_data(coverage_data)

    # Format and return
    return (linesep * 2).join(list(filter(lambda c: c, map(lambda p: format_category(pargs, known_paths, p), sorted(coverage_data.items(), key=fst)))))

def format_category(pargs, known_paths:[str], coverage_data:tuple) -> str:
    formatted_table:str = make_table(pargs, known_paths, coverage_data[1])
    return linesep.join([coverage_data[0] + ':', formatted_table]) if formatted_table else ''

def make_table(pargs:Namespace, known_paths:[str], table_data:[dict]) -> str:
    if table_data == []:
        return ''

    # Prep table
    table:BeautifulTable = BeautifulTable()

    # Add header
    col_names:[str] = list(map(str, table_data[0].keys()))
    col_names_order:dict = { c:p for p,c in enumerate(col_names) }
    table.columns.header = list(map(lambda c: apply_formatting(pargs, formats.header_format, c), col_names))

    # Add table body content
    body:[[object]] = list(map(lambda r: list(map(lambda f: _format_field(pargs, known_paths, f[1]), r)), map(lambda r: list(sorted(r.items(), key=lambda p: col_names_order[p[0]])), table_data)))
    for record in body:
        table.rows.append(record)

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

    return str(table)

def _format_field(pargs:Namespace, known_paths:[str], val:object) -> str:
    convs:dict = {
        int: lambda i: apply_formatting(pargs, formats.num_format, str(i)),
        float: lambda f: apply_formatting(pargs, formats.num_format, '%%.%df' % float_output_precision % f),
        str: lambda s: format_str(pargs, known_paths, s),
        bool: lambda b: apply_formatting(pargs, formats.tick_format, '✓') if b else apply_formatting(pargs, formats.cross_format, '✗'),
        set: lambda s: apply_formatting(pargs, formats.empty_set_format, formats.empty_set_string) if len(s) == 0 else '{ %s }' % format_list(pargs, known_paths, s),
        tuple: lambda t: format_list(pargs, known_paths, t),
        list: lambda l: format_list(pargs, known_paths, l),
        dict: lambda d: format_list(pargs, known_paths, list(map(lambda p: '%s=%s' % p, d.items()))),
        type(None): lambda _: apply_formatting(pargs, formats.none_format, formats.none_string)
    }
    return convs[type(val)](val)

def format_str(pargs:Namespace, known_paths:[str], s:str) -> str:
    if not s:
        return apply_formatting(pargs, formats.empty_string_format, formats.empty_string_string)
    def format_word(pargs:Namespace, known_paths:[str], s:str) -> str:
        if s in known_paths or (pargs.input_dir and s.startswith(pargs.input_dir)) or (pargs.target_dir and s.startswith(pargs.target_dir)) or s[-4:] in ['.json', '.yml', '.yaml'] or s.endswith(sep):
            return apply_formatting(pargs, formats.path_format, s)
        if match(keycap_pretty_name_regex, s) is not None:
            return apply_formatting(pargs, formats.keycap_name_format, s)
        return s
    return ' '.join(list(map(lambda w: format_word(pargs, known_paths, w), s.split())))

def format_list(pargs:Namespace, known_paths:[str], l:list) -> str:
    if l == []:
        return apply_formatting(pargs, formats.empty_list_format, formats.empty_list_string)
    return ', '.join(list(map(lambda v: _format_field(pargs, known_paths, v), l)))

def apply_formatting(pargs:Namespace, formatting:int, s:str) -> str:
    if not use_colour(pargs):
        return s

    formatting_codes:str = ''
    formats_to_apply:[str]
    if type(formatting) == list:
        formats_to_apply = formatting
    else:
        formats_to_apply = [formatting]
    for format_to_apply in formats_to_apply:
        formatting_codes += '\033[' + terminal_formats[format_to_apply]

    end_formatting:str = END_CODE if formatting_codes else ''
    return formatting_codes + s + end_formatting

def use_colour(pargs:Namespace, file=stdout) -> bool:
    plat:str = platform
    supported_platform:bool = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in environ)
    # isatty is not always implemented, but it'll have to do.
    is_a_tty:bool = hasattr(file, 'isatty') and file.isatty()

    if pargs.force_colour:
        return True
    if pargs.force_no_colour:
        return False
    return supported_platform and is_a_tty

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
