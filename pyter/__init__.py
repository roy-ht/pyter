# -*- coding:utf-8 -*-
""" Copyright (c) 2011 Hiroyuki Tanaka. All rights reserved."""

# TODO: This syntax will be supported forever?
from __future__ import division
import itertools as itrt
import operator

def ter_align(ref_input, hyp_input, wordmatch=True):
    """ aligning via Translation Error Rate matching algorithm.
    >>> ter_align(''
    """
    ref = _str2list(ref_input, wordmatch)
    hyp = _str2list(hyp_input, wordmatch)
    if len(ref) > len(hyp):
        hyp += [''] * (len(ref) - len(hyp))
    dist = lambda x, y: edit_distance(x, list(filter(None, y)))
    ## prepare align
    h = hyp
    marks = {}
    replaced_map = list(range(len(hyp)))  ## trace replacing
    while True:
        ## find the alignment
        scores = []
        for csr, sp, ep in _iter_matches(ref, h):
            nhyp = h[:sp] + h[ep:]
            nhyp = nhyp[:csr] + h[sp:ep] + nhyp[csr:]
            scores.append((dist(ref, nhyp), nhyp, csr, sp, ep))
        if not scores:
            break
        scores.sort()
        scores = [x for x in scores if  x[0] == scores[0][0]]
        scores.sort(key=lambda x: x[4] - x[3], reverse=True)
        prescore = dist(ref, h)
        if scores[0][0] >= prescore:
            break
        # post scoreing
        h = scores[0][1]
        csr, sp, ep = scores[0][2:]
        hyp_mark = replaced_map[sp:ep]
        nrmap = replaced_map[:sp] + replaced_map[ep:]
        nrmap = nrmap[:csr] + replaced_map[sp:ep] + nrmap[csr:]
        replaced_map = nrmap
        marks[csr] = hyp_mark
    ## do align
    aligns = [(x, y[0], len(y)) for x, y in marks.items()]
    hyp_indexes = set(range(len(hyp)))
    for _, l in marks.items():
        hyp_indexes -= set(l)
    hyp_indexes = sorted(list(hyp_indexes))
    sp = 0
    while sp < len(ref):
        if sp in marks:
            sp += len(marks[sp])
            continue
        # 最初にhyp_indexesにヒットするindexは
        h_sp = None
        for idx in (i for i, x in enumerate(hyp) if x == ref[sp]):
            if idx in hyp_indexes:
                h_sp = idx
                break
        if h_sp is None:
            sp += 1
            continue
        for h_ep in range(h_sp + 1, len(hyp) + 1):
            if h_ep == len(hyp) or sp + h_ep - h_sp >= len(ref) or hyp[h_ep] != ref[sp + h_ep - h_sp]:
                aligns.append((sp, h_sp, h_ep - h_sp))
                sp += h_ep - h_sp
                break
        else:
            assert(False)  # must not come here
    aligns.sort()
    ## re formulate to string index
    if wordmatch:
        aligns = [(sum(len(x) + 1 for x in ref[:y]),
                   sum(len(x) + 1 for x in hyp[:z]),
                   sum(len(x) + 1 for x in ref[y:y + w]) - 1)
                   for y, z, w in aligns]
    return aligns

def ter(ref, hyp, wordmatch=True):
    """Calcurate Translation Error Rate
    if wordmatch is True, input sentences are regarded as space separeted word sequence.
    else, input sentences are matched with each characters.
    >>> ref = 'SAUDI ARABIA denied THIS WEEK information published in the AMERICAN new york times'
    >>> hyp = 'THIS WEEK THE SAUDIS denied information published in the new york times'
    >>> '%.3f' % ter(ref, hyp)
    '0.308'
    """
    ref = _str2list(ref, wordmatch)
    hyp = _str2list(hyp, wordmatch)
    return _ter(ref, hyp, edit_distance)


def ter_glue(ref, hyp, wordmatch=True):
    """ When len(ref) > len(hyp), ter cannnot shift the words of ref[len(hyp):].
    ter_glue allow to add the "glue" in to the hyp, and remove this limitation.
    >>> ref = 'SAUDI ARABIA denied THIS WEEK information published in the AMERICAN new york times'
    >>> hyp = 'THIS WEEK THE SAUDIS denied information published in the new york times'
    >>> ter_glue(ref, hyp) == ter(ref, hyp)
    True
    """
    ref = _str2list(ref, wordmatch)
    hyp = _str2list(hyp, wordmatch)
    if len(ref) > len(hyp):
        hyp += [''] * (len(ref) - len(hyp))
    mtd = lambda x, y: edit_distance(x, list(filter(None, y)))
    return _ter(ref, hyp, mtd)


def _str2list(s, wordmatch=True):
    """ Split the string into list """
    return s.split() if wordmatch else list(s)
        

def _ter(ref, hyp, mtd):
    """ Translation Erorr Rate core function """
    err = 0
    while True:
        (delta, hyp) = _shift(ref, hyp, mtd)
        if delta == 0:
            break
        err += 1
    return (err + mtd(ref, hyp)) / len(ref)
    

def _shift(ref, hyp, mtd):
    """ Shift the phrase pair most reduce the edit_distance
    Return True shift occurred, else False.
    """
    pre_score = mtd(ref, hyp)
    scores = []
    for csr, sp, ep in _iter_matches(ref, hyp):
        nhyp = hyp[:sp] + hyp[ep:]
        nhyp = nhyp[:csr] + hyp[sp:ep] + nhyp[csr:]
        scores.append((mtd(ref, nhyp), nhyp))
    if not scores:
        return (0, hyp)
    scores.sort()
    return (scores[0][0] - pre_score, scores[0][1]) if scores[0][0] < pre_score else (0, hyp)


def _iter_matches(ref, hyp):
    """ yield the tuple of (ref_start_point, hyp_start_point, hyp_end_point)
    for all possible shiftings.
    """
    # refの位置に置き換えるのだから、短い方のsequenceに合わせる
    maxlen = min(len(ref), len(hyp))
    for csr in range(maxlen):
        # already aligned
        if ref[csr] == hyp[csr]:
            continue
        # search start point
        for sp in range(maxlen):
            if csr != sp and ref[csr] == hyp[sp]:
                # found start point of matched phrase
                for ep in range(sp + 1, maxlen + 1):
                    if ep == maxlen or csr + ep - sp == len(ref) or ref[csr + ep - sp] != hyp[ep]:
                        yield (csr, sp, ep)
                        break
                else:
                    # must break
                    assert(False)
    


def edit_distance(s, t):
    """It's same as the Levenshtein distance"""
    l = gen_matrix(len(s) + 1, len(t) + 1, None)
    l[0] = [x for x, _ in enumerate(l[0])]
    for x, y in enumerate(l):
        y[0] = x
    for i, j in itrt.product(range(1, len(s) + 1), range(1, len(t) + 1)):
        l[i][j] = min(l[i - 1][j] + 1,
                      l[i][j - 1] + 1,
                      l[i - 1][j - 1] + (0 if s[i - 1] == t[j - 1] else 1))
    return l[-1][-1]


def gen_matrix(col_size, row_size, default=None):
    return [[default for _ in range(row_size)] for __ in range(col_size)]


#################
## not used now
#################

def diagonal_scanner(col_size, row_size, reverse=False):
    """diagonal index access for a matrix
    if reverse is True, Change scanning direction from left down to left up
    >>> list(diagonal_scanner(2, 2))
    [(0, 0), (0, 1), (1, 0), (1, 1)]
    >>> list(diagonal_scanner(3, 2))
    [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    >>> list(diagonal_scanner(2, 3))
    [(0, 0), (0, 1), (1, 0), (0, 2), (1, 1), (1, 2)]
    >>> list(diagonal_scanner(0, 1))
    Traceback (most recent call last):
        ...
    ValueError: Argment 1 and 2 must be larger than 0.
    >>> list(diagonal_scanner(2, 3, reverse=True))
    [(1, 0), (1, 1), (0, 0), (1, 2), (0, 1), (0, 2)]
    """
    stti, sttj = 0, 0
    endi, endj = col_size, row_size
    if stti >= endi or sttj >= endj:
        raise ValueError("Argment 1 and 2 must be larger than 0.")
    cursor = [0, 0]
    while cursor[0] < endi and cursor[1] < endj:
        for i in itrt.count():
            r = (cursor[0] + i, cursor[1] - i)
            yield (col_size - 1 - r[0], r[1]) if reverse else r
            if r[0] == col_size - 1 or r[1] == 0:
                break
        if cursor[1] < row_size - 1:
            cursor[1] += 1
        else:
            cursor[0] += 1
        
