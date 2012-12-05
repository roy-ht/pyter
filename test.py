# -*- coding:utf-8 -*-

import pyter

def test_same():
    s = '''Since the visigoth period, the term Hispania, up until then used geographically, began to be also used with a political connotation, as an example the use of the expression Laus Hispaniae  to describe the history of the towns of the peninsula in the chronicles of Isodoro de Sevilla.'''
    assert pyter.ter(s.split(), s.split()) == 0

def test_paper():
    ref = 'SAUDI ARABIA denied THIS WEEK information published in the AMERICAN new york times'.split()
    hyp = 'THIS WEEK THE SAUDIS denied information published in the new york times'.split()
    assert 0.3076923076923077 == pyter.ter(hyp, ref)
