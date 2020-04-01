from toolz import keyfilter, itemmap
from itertools import zip_longest
from typing import Callable, Collection, Dict, Tuple


def fextract(keys: Collection, data_dict: Dict) -> Dict:
    """
    Extracts (key, value) pairs from d if key is in keys
    :param keys: a collection, should support __contains__
    :param data_dict: a data dictionary
    :return: a data dictionary
    """
    return keyfilter(
        lambda k: k in keys, data_dict
    )


def flookup(lookup_map: Dict, keys: Collection, data_dict: Dict) -> Dict:
    result = keyfilter(lambda k: k not in keys, data_dict)
    for key in keys:
        if key in data_dict:
            if data_dict[key] in lookup_map:
                result[key] = lookup_map[data_dict[key]]  # found ! :D
            else:
                result[key] = None  # not found :'(
        else:
            pass  # field does not exist :/

    return result


def freverse_lookup(lookup_map: Dict, keys: Collection,
                    data_dict: Dict) -> Dict:
    result = keyfilter(lambda k: k not in keys, data_dict)
    for key in keys:
        if key in data_dict:
            for item in lookup_map:
                if data_dict[key] in lookup_map[item]:
                    result[key] = item  # found ! :D
                    break
            else:
                result[key] = None  # not found :'(
        else:
            pass  # field does not exist :/

    return result


def fmap(keys: Collection, funcs: Collection[Callable],
         data_dict: Dict, val_as_args: bool = False) -> Dict:
    """

    :param keys: a collection, should support __contains__
                 and __getitem__
    :param funcs: a iterable of callables
    :param data_dict: a data dictionary
    :param val_as_args: bool
    :return: a data dictionary
    """
    func_map = dict(
        zip_longest(
            keys, funcs,
            fillvalue=lambda x: x
        )
    )

    def _apply_func(item):
        k, v = item
        if k in func_map:
            if val_as_args:
                return k, func_map[k](*v)
            else:
                return k, func_map[k](v)
        else:
            return k, v

    return dict(
        itemmap(_apply_func, data_dict)
    )


def fremove(keys: Collection, data_dict: Dict) -> Dict:
    """
    Remove keys according to a list
    :param keys:
    :param data_dict:
    :return:
    """
    return keyfilter(
        lambda k: k not in keys,
        data_dict
    )


def frename(keys: Collection, data_dict: Dict) -> Dict:
    """
    Rename keys according to a mapping
    :param keys:
    :param data_dict:
    :return:
    """
    def _keys(item):
        k, v = item
        if k in keys:
            return keys[k], v
        else:
            return k, v

    return dict(
        itemmap(_keys, data_dict)
    )


def fsplit(keys: Collection, data_dict: Dict) -> Tuple[Dict, Dict]:
    return fextract(keys, data_dict), fremove(keys, data_dict)
