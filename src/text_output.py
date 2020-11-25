from .args import Namespace
from .util import repeat
from beautifultable import ALIGN_LEFT, BeautifulTable
from os import environ, linesep
from shutil import get_terminal_size
from sys import platform, stdout
from typing import Tuple

default_terminal_size:Tuple[int, int] = (80, 24)

PURPLE:int = 0x1
CYAN:int = 0x2
DARKCYAN:int = 0x4
BLUE:int = 0x8
GREEN:int = 0x10
YELLOW:int = 0x20
RED:int = 0x40
BOLD:int = 0x80
UNDERLINE:int = 0x100

terminal_formats:dict = {
    PURPLE: '\033[95m',
    CYAN: '\033[96m',
    DARKCYAN: '\033[36m',
    BLUE: '\033[94m',
    GREEN: '\033[92m',
    YELLOW: '\033[93m',
    RED: '\033[91m',
    BOLD: '\033[1m',
    UNDERLINE: '\033[4m',
}
END_CODE = '\033[0m'

TICK_FORMAT:int = GREEN
CROSS_FORMAT:int = RED
NUM_FORMAT:int = DARKCYAN
HEADER_FORMAT:int = BOLD | BLUE
PATH_FORMAT:int = UNDERLINE
EMPTY_STRING_FORMAT:int = BOLD | RED
EMPTY_STRING_STRING:str = '/'
EMPTY_LIST_FORMAT:int = EMPTY_STRING_FORMAT
EMPTY_LIST_STRING:str = EMPTY_STRING_STRING
NONE_FORMAT:int = RED
NONE_STRING:str = '-'

float_output_precision:int = 2

def output_as_text(pargs:Namespace, coverage_data:dict) -> str:
    return (linesep * 2).join(list(map(lambda c: format_category(pargs, c), coverage_data.values())))

def format_category(pargs:Namespace, coverage_data:tuple) -> str:
    return make_table(pargs, coverage_data)

def make_table(pargs:Namespace, table_data:[dict]) -> str:
    if table_data == []:
        return ''

    # Prep table
    table:BeautifulTable = BeautifulTable()

    # Add header
    col_names:[str] = list(map(str, table_data[0].keys()))
    col_names_order:dict = { c:p for p,c in enumerate(col_names) }
    table.columns.header = list(map(lambda c: apply_formatting(pargs, HEADER_FORMAT, c), col_names))

    # Add table body content
    body:[[object]] = list(map(lambda r: list(map(lambda f: _format_field(pargs, f[1]), r)), map(lambda r: list(sorted(r.items(), key=lambda p: col_names_order[p[0]])), table_data)))
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
    table.maxwidth = get_terminal_size(default_terminal_size).columns

    return str(table)

def _format_field(pargs:Namespace, val:object) -> str:
    convs:dict = {
        int: lambda i: apply_formatting(pargs, NUM_FORMAT, str(i)),
        float: lambda f: apply_formatting(pargs, NUM_FORMAT, ('%%.%df' % float_output_precision) % f),
        str: lambda s: format_str(pargs, s),
        bool: lambda b: apply_formatting(pargs, TICK_FORMAT, '✓') if b else apply_formatting(pargs, CROSS_FORMAT, '✗'),
        list: lambda l: format_list(pargs, l),
        type(None): lambda _: apply_formatting(pargs, NONE_FORMAT, NONE_STRING)
    }
    return convs[type(val)](val)

def format_str(pargs:Namespace, s:str) -> str:
    if (pargs.input_dir and s.startswith(pargs.input_dir)) or (pargs.target_dir and s.startswith(pargs.target_dir)) or s[-4:] in ['.json', '.yml', '.yaml']:
        return apply_formatting(pargs, PATH_FORMAT, s)
    if not s:
        return apply_formatting(pargs, EMPTY_STRING_FORMAT, EMPTY_STRING_STRING)
    return s

def format_list(pargs:Namespace, l:list) -> str:
    if l == []:
        return apply_formatting(pargs, EMPTY_LIST_FORMAT, EMPTY_LIST_STRING)
    return ', '.join(list(map(lambda v: _format_field(pargs, v), l)))

def apply_formatting(pargs:Namespace, formatting:int, s:str) -> str:
    if not use_colour(pargs):
        return s

    formatting_codes:str = ''
    for terminal_format in terminal_formats:
        if formatting & terminal_format:
            formatting_codes += terminal_formats[terminal_format]
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
