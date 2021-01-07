from .util import iconcat
from functools import reduce
from os import walk as owalk
from os.path import exists, isdir, isfile, join, splitext
from sys import stderr
from typing import List, Union

def get_json_and_yaml_files(path:Union[str, List[str]]) -> [str]:
    if type(path) == list:
        return list(reduce(iconcat, map(get_json_and_yaml_files, path)))
    elif isdir(path):
        return list(filter(lambda f: splitext(f)[1].lower() in ['.yml', '.yaml', '.json'], walk(path)))
    elif isfile(path):
        return [path]
    else:
        print('Could not find file or directory "%s"' % path, file=stderr)
        exit(-1)

def walk(dname:str) -> [str]:
    ret:[str] = []
    for (r,_,fs) in owalk(dname):
        ret.extend(map(lambda f: join(r,f), fs))
    return ret
