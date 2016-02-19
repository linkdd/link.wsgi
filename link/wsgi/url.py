# -*- coding: utf-8 -*-

from six.moves.urllib.parse import parse_qs as base_parse_qs


def parse_qs(query):
    """
    Override six.moves.urllib.parse.parse_qs to handle array parameters
    """

    result = {}
    tmp = base_parse_qs(query)

    for key in tmp:
        if key.endswith('[]'):
            result[key[:-2]] = tmp[key]

        else:
            result[key] = tmp[key][0]

    return result
