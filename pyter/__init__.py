# -*- coding:utf-8 -*-
from __future__ import division, print_function
""" Copyright (c) 2011 Hiroyuki Tanaka. All rights reserved."""
import itertools as itrt
import bisect
from pyter import util


def ter(inputwords, refwords):
    """Calcurate Translation Error Rate
    inputwords and refwords are both list object.
    >>> ref = 'SAUDI ARABIA denied THIS WEEK information published in the AMERICAN new york times'.split()
    >>> hyp = 'THIS WEEK THE SAUDIS denied information published in the new york times'.split()
    >>> '{0:.3f}'.format(ter(hyp, ref))
    '0.308'
    """
    inputwords, refwords = list(inputwords), list(refwords)
    ed = FastEditDistance(refwords)
    return _ter(inputwords, refwords, ed)


def _ter(iwords, rwords, mtd):
    """ Translation Erorr Rate core function """
    err = 0
    # print('[I]', u' '.join(iwords))
    # print('[R]', u' '.join(rwords))
    # print('[ED]', mtd(iwords))
    while True:
        (delta, iwords) = _shift(iwords, rwords, mtd)
        # print('[I]', u' '.join(iwords))
        # print('[R]', u' '.join(rwords))
        # print('[ED]', mtd(iwords))
        if delta <= 0:
            break
        err += 1
    # print(err, mtd(iwords), len(rwords), (err + mtd(iwords)) / len(rwords))
    return (err + mtd(iwords)) / len(rwords)


def _shift(iwords, rwords, mtd):
    """ Shift the phrase pair most reduce the edit_distance
    Return True shift occurred, else False.
    """
    pre_score = mtd(iwords)
    scores = []
    for isp, rsp, length in _findpairs(iwords, rwords):
        shifted_words = iwords[:isp] + iwords[isp + length:]
        shifted_words[rsp:rsp] = iwords[isp:isp + length]
        scores.append((pre_score - mtd(shifted_words), shifted_words))
    if not scores:
        return (0, iwords)
    scores.sort()
    return scores[-1]


def _findpairs(ws1, ws2):
    u""" yield the tuple of (ws1_start_point, ws2_start_point, length)
    So ws1[ws1_start_point:ws1_start_point+length] == ws2[ws2_start_point:ws2_start_point+length]
    """
    for i1, i2 in itrt.product(range(len(ws1)), range(len(ws2))):
        if i1 == i2:
            continue  # take away if there is already in the same position
        if ws1[i1] == ws2[i2]:
            # counting
            length = 1
            for j in range(1, len(ws1) - i1):
                j1, j2 = i1 + j, i2 + j
                if j2 < len(ws2) and ws1[j1] == ws2[j2]:
                    length += 1
                else:
                    break
            yield (i1, i2, length)


def _gen_matrix(col_size, row_size, default=None):
    return [[default for _ in range(row_size)] for __ in range(col_size)]


def edit_distance(s, t):
    """It's same as the Levenshtein distance"""
    l = _gen_matrix(len(s) + 1, len(t) + 1, None)
    l[0] = [x for x, _ in enumerate(l[0])]
    for x, y in enumerate(l):
        y[0] = x
    for i, j in itrt.product(range(1, len(s) + 1), range(1, len(t) + 1)):
        l[i][j] = min(l[i - 1][j] + 1,
                      l[i][j - 1] + 1,
                      l[i - 1][j - 1] + (0 if s[i - 1] == t[j - 1] else 1))
    return l[-1][-1]



class FastEditDistance(object):
    """<Experimental> Cached edit distance to calculate similar two strings.
    ref and hyp must be list or string, not generetor.
    Cache stored input hypothesis with each elements.
    """
    def __init__(self, ref):
        self.ref = ref
        self.cache_keys = []
        self.cache_value = []
        self.trivial_list = [list(range(len(ref) + 1))]

    def __call__(self, hyp):
        condition, resthyp = self._find_cache(hyp)
        new_cache, score = self._edit_distance(resthyp, condition)
        self._add_cache(new_cache, hyp)
        return score

    def _find_cache(self, hyp):
        """find longest common prefix, and return prefix of hit cache
        """
        idx = bisect.bisect_left(self.cache_keys, hyp)
        cplen_pre = 0 if idx == 0 else self._common_prefix_index(self.cache_keys[idx - 1], hyp)
        cplen_pos = 0 if idx == len(self.cache_keys) else self._common_prefix_index(self.cache_keys[idx], hyp)
        if cplen_pre > cplen_pos:
            return self.cache_value[idx - 1][:cplen_pre + 1], hyp[cplen_pre:]
        elif cplen_pre < cplen_pos:
            return self.cache_value[idx][:cplen_pos + 1], hyp[cplen_pos:]
        elif cplen_pre > 0:
            return self.cache_value[idx - 1][:cplen_pre + 1], hyp[cplen_pre:]
        return  self.trivial_list, hyp

    def _add_cache(self, ncache, s):
        """insert cache with sorted order, using binary search
        """
        idx = bisect.bisect_left(self.cache_keys, s)
        if idx < len(self.cache_keys) - 1 and self.cache_keys[idx + 1] == s:
            return              # don't have to add
        self.cache_keys.insert(idx, s)
        self.cache_value.insert(idx, ncache)

    def _common_prefix_index(self, s, t):
        """ Return end of common prefix index.
        """
        r = 0
        for i in range(min(len(s), len(t))):
            if s[i] != t[i]:
                break
            r += 1
        return r

    def _edit_distance(self, hyp, cond):
        """ calculate edit distance.
        """
        offset = len(cond)
        l = cond + [[None for _ in range(len(self.ref) + 1)] for __ in range(len(hyp))]
        for i, j in itrt.product(range(offset, offset + len(hyp)), range(len(self.ref) + 1)):
            if j == 0:
                l[i][j] = l[i - 1][j] + 1
            else:
                l[i][j] = min(l[i - 1][j] + 1,
                              l[i][j - 1] + 1,
                              l[i - 1][j - 1] + (0 if hyp[i - offset] == self.ref[j - 1] else 1))
        return l, l[-1][-1]


def parse_args():
    import argparse             # new in Python 2.7!!
    parser = argparse.ArgumentParser(
        description='Translation Error Rate Evaluator',
        epilog="If you have an UnicodeEncodeError, try to set 'PYTHONIOENCODING' to your environment variables."
        )
    parser.add_argument('-r', '--ref', help='Reference file', required=True)
    parser.add_argument('-i', '--input', help='Input(test) file', required=True)
    parser.add_argument('-v', '--verbose', help='Show scores of each sentence.',
                        action='store_true', default=False)
    parser.add_argument('-l', '--lang', choices=['ja', 'en'], default='en', help='Language')
    parser.add_argument('--force-token-mode', action='store_true', default=False, help='Use a space separated word as a unit')
    return parser.parse_args()


def main():
    import codecs
    import sys
    import itertools
    import math
    args = parse_args()
    ilines = [util.preprocess(x, args.lang) for x in codecs.open(args.input, 'r', 'utf-8').readlines()]
    rlines = [util.preprocess(x, args.lang) for x in codecs.open(args.ref, 'r', 'utf-8').readlines()]
    if len(ilines) != len(rlines):
        print("Error: input file has {0} lines, but reference has {1} lines.".format(len(ilines), len(rlines)))
        sys.exit(1)
    scores = []
    for lineno, (rline, iline) in enumerate(itertools.izip(ilines, rlines), start=1):
        if args.force_token_mode:
            rline, iline = rline.split(), iline.split()
        else:
            rline, iline = util.split(rline, args.lang), util.split(iline, args.lang)
        # iline, rline are list object
        score = ter(iline, rline)
        scores.append(score)
        if args.verbose:
            print("Sentence {0}: {1:.4f}".format(lineno, score))
    average = sum(scores) / len(scores)
    variance = sum((x - average) ** 2 for x in scores) / len(scores)
    stddev = math.sqrt(variance)
    print("Average={0:.4f}, Variance={1:.4f}, Standard Deviatioin={2:.4f}".format(average, variance, stddev))


if __name__ == '__main__':
    main()
