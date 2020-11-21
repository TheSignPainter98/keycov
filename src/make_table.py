from texttable import Texttable as TextTable

def make_table(table_data:[dict], sort_key:str=None) -> str:
    if table_data == []:
        return ''

    # Prep table
    table:TextTable = TextTable()
    num_cols:int = len(table_data[0].keys())

    # Set styling
    table.set_deco(TextTable.HEADER)
    table.set_chars(['─', '│', '┼', '─'])
    table.set_header_align(repeat('l', num_cols))
    table.set_cols_dtype(repeat(_format_field, num_cols))

    # Apply header
    col_names:[str] = list(map(str, table_data[0].keys()))
    col_names_order:dict = { c:p for p,c in enumerate(col_names) }
    table.header(col_names)

    # Add table body content
    body:[[object]] = list(map(lambda r: list(map(lambda f: f[1], r)), sorted(map(lambda r: list(sorted(r.items(), key=lambda p: col_names_order[p[0]])), table_data), key=sort_key)))
    table.add_rows(body, header=False)

    return table.draw()

def _format_field(val:object) -> str:
    convs:dict = {
        int: str,
        float: lambda f: '%.2f' % f,
        str: lambda s: s,
        bool: bool,
        list: lambda l: ', '.join(list(map(_format_field,l)))
    }
    return convs[type(val)](val)

def repeat(val:object, n:int) -> [object]:
    return [ val for _ in range(n) ]
