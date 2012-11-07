# -*- coding:utf-8 -*-
from __future__ import division, print_function
""" Copyright (c) 2011 Hiroyuki Tanaka. All rights reserved."""

from pyter import util
from .ter import *

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
    parser.add_argument('-g', '--glue', help='glue mode (one of the scoring algorithm)',
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
    ilines = [util.preprocess(x, args.lang) for x in codecs.open(opts.input, 'r', 'utf-8').readlines()]
    rlines = [util.preprocess(x, args.lang) for x in codecs.open(opts.ref, 'r', 'utf-8').readlines()]
    if len(ilines) != len(rlines):
        print("Error: input file has {0} lines, but reference has {1} lines.".format(len(ilines), len(rlines)))
        sys.exit(1)
    scores = []
    score_method = ter_glue if args.glue else ter
    for lineno, (rline, iline) in enumerate(itertools.izip(ilines, rlines), start=1):
        if args.force_token_mode:
            rline, iline = rline.split(), iline.split()
        else:
            rline, iline = util.split(rline, args.lang), util.split(iline.args.lang)
        # iline, rline are list object
        score = score_method(iline, rline)
        scores.append(score)
        if opts.verbose:
            print("Sentence {0}: {0:4f}".format((lineno, score)))
    average = sum(scores) / len(scores)
    variance = sum((x - average) ** 2 for x in scores) / len(scores)
    stddev = math.sqrt(variance)
    print("Average={0:4f}, Variance={1:4f}, Standard Deviatioin={2:4f}".format(average, variance, stddev))


if __name__ == '__main__':
    main()
