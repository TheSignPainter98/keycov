from .args import Namespace
from .util import repeat
from os import environ, linesep
from sys import platform, stdout
from texttable import Texttable as TextTable

PURPLE = 0x1
CYAN = 0x2
DARKCYAN = 0x4
BLUE = 0x8
GREEN = 0x10
YELLOW = 0x20
RED = 0x40
BOLD = 0x80
UNDERLINE = 0x100

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

float_output_precision:int = 2

def output_as_text(pargs:Namespace, coverage_data:dict) -> str:
    return (linesep * 2).join(list(map(lambda c: format_category(pargs, c), coverage_data.values())))

def format_category(pargs:Namespace, coverage_data:tuple) -> str:
    return make_table(pargs, coverage_data)

def make_table(pargs:Namespace, table_data:[dict]) -> str:
    if table_data == []:
        return ''

    # Prep table
    table:TextTable = TextTable()
    num_cols:int = len(table_data[0].keys())

    # Set styling
    table.set_deco(TextTable.HEADER)
    table.set_chars(['─', '│', '┼', '─'])
    table.set_header_align(repeat('l', num_cols))
    table.set_cols_dtype(repeat(lambda f: _format_field(pargs, f), num_cols))
    table.set_precision(float_output_precision)

    # Apply header
    col_names:[str] = list(map(str, table_data[0].keys()))
    col_names_order:dict = { c:p for p,c in enumerate(col_names) }
    formatted_col_names:[str] = list(map(lambda c: apply_formatting(pargs, 0, c), col_names))
    table.header(formatted_col_names)

    # Add table body content
    body:[[object]] = list(map(lambda r: list(map(lambda f: f[1], r)), map(lambda r: list(sorted(r.items(), key=lambda p: col_names_order[p[0]])), table_data)))
    table.add_rows(body, header=False)

    return table.draw()

def _format_field(pargs:Namespace, val:object) -> str:
    convs:dict = {
        int: str,
        float: lambda f: ('%%.%df' % float_output_precision) % f,
        str: lambda s: s,
        bool: lambda b: apply_formatting(pargs, TICK_FORMAT, '✓') if b else apply_formatting(pargs, CROSS_FORMAT, '✗'),
        list: lambda l: ', '.join(list(map(lambda v: _format_field(pargs, v), l))),
        type(None): lambda _: ''
    }
    return convs[type(val)](val)

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
