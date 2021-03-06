from functools import reduce
from typing import Callable, Tuple

default_text_colour:str = '#000000'
default_cap_colour:str = '#cccccc'

default_terminal_dims:Tuple[int, int] = (80, 24)
special_properties:dict = {
    'H': lambda k: k['n'],
    'I': lambda k: k['w'] == 1.25 \
        and k['h'] == 2 \
        and k['w2'] == 1.5 \
        and k['h2'] == 1 \
        and k['x2'] == -0.25,
    'S': lambda k: k['l'],
}


def flatten(obj:object) -> [object]:
    if type(obj) == list:
        return reduce(iconcat, map(flatten, obj), [])
    else:
        return [obj]

def concat(a:list, b:list) -> list:
    return a + b

def iconcat(a:list, b:list) -> list:
    a.extend(b)
    return a

def repeat(val:object, n:int) -> [object]:
    return [ val for _ in range(n) ]

def restrict_dict(d:dict, ks:[object]) -> dict:
    return { k:v for k,v in d.items() if k in ks }

def fst(p:tuple) -> object:
    return p[0]

def snd(p:tuple) -> object:
    return p[1]

def swp(p:tuple) -> tuple:
    return (p[0], p[1])

def dict_union_ignore_none(a: dict, b: dict) -> dict:
    return dict(a, **dict(filter(lambda p: p[1] is not None, b.items())))

def dict_union(*ds:[dict]) -> dict:
    def _dict_union(a:dict, b:dict) -> dict:
        return dict(a, **b)
    return dict(reduce(_dict_union, ds, {}))

def add(a:object, b:object) -> object:
    return a + b

def mult(a:object, b:object) -> object:
    return a * b

def serialise_key(key:dict) -> str:
    return key_pretty_name(key)

def key_pretty_name(key:dict) -> str:
    name:str = key['key'].replace('\n', '_').replace(' ', '+')
    dimensions:str = '%.2fx%.2f' %(key['w'], key['h'])
    if (key['w2'] != key['w'] or key['h2'] != key['h']) and (key['w2'] != 1.0 or key['h2'] != 1.0):
        dimensions += '[%.2fx%.2f]' % (key['w2'], key['h2'])
    key_props:str = ''
    for flag,cond in sorted(special_properties.items(), key=fst):
        if cond(key):
            key_props += flag
    key_colours:[str] = []
    for colour_key,pretty_colour_key,default_colour in [('c', '𝕔', default_cap_colour), ('t', '𝕥', default_text_colour)]:
        if key[colour_key] != default_colour:
            key_colours.append(pretty_colour_key + key[colour_key])

    return '-'.join([name, dimensions] + ([key_props] if key_props else []) + key_colours)

def compose(f:Callable, g:Callable) -> Callable:
    return lambda x: f(g(x))

def notf(c:bool) -> bool:
    return not c
