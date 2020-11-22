from functools import reduce

def flatten(obj:object) -> [object]:
    if type(obj) == list:
        return reduce(iconcat, map(flatten, obj), [])
    else:
        return [obj]

def iconcat(a:list, b:list) -> list:
    a.extend(b)
    return a

def repeat(val:object, n:int) -> [object]:
    return [ val for _ in range(n) ]
