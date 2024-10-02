"""Utility functions for components."""
from itertools import chain, combinations
import spot
from collections import OrderedDict as od


def powerset(s):
    if type(s)==list:
        s = list(s)
    ps = list(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))
    return ps

def neg(formula):
    return spot.formula.Not(formula)

def conjunction(formula_list):
    return spot.formula.And(formula_list)

def disjunction(formula_list):
    return spot.formula.Or(formula_list)


def get_states_and_transitions_from_file(mazefile):
    map = od()
    f = open(mazefile, 'r')
    lines = f.readlines()
    len_z = len(lines)
    for i,line in enumerate(lines):
        for j,item in enumerate(line):
            if item != '\n' and item != '|':
                map[i,j] = item
                len_x = j
    len_x += 1

    states = []
    goal = [] # update this to use the labels?
    for z in range(0,len_z):
        for x in range(0,len_x):
            if map[(z,x)] != '*':
                states.append(((z,x)))
                if map[(z,x)] == 'S':
                    init = (z,x)
                if map[(z,x)] == 'T':
                    goal.append((z,x))

    transitions_dict = dict()
    for node in states:
        next_states = [(node[0], node[1])]
        if node not in goal:
            for a in [-1,1]: # can always move horizontally!
                if (node[0],node[1]+a) in states:
                    next_states.append((node[0], node[1]+a))
            for b in [-1,1]: # can always move vertically!
                if (node[0]+b,node[1]) in states:
                    next_states.append((node[0]+b, node[1]))
        transitions_dict.update({node: next_states})
    return states, transitions_dict
