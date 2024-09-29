import json
import ast
import argparse

from flowsynth.optimization.optimize import solve
from flowsynth.components.automata import get_system_automaton, get_tester_automaton, get_product_automaton
from flowsynth.components.transition_system import TranSys, TransitionSystemInput
from flowsynth.components.product import sync_prod
from flowsynth.components.utils import get_states_and_transitions_from_file

from ipdb import set_trace as st

def get_automata(sys_formula, test_formula):
    # get automata
    sys_aut, spot_aut_sys = get_system_automaton(sys_formula)
    test_aut, spot_aut_test = get_tester_automaton(test_formula)
    prod_aut = get_product_automaton(spot_aut_sys, spot_aut_test)
    return sys_aut, test_aut, prod_aut

def get_transition_system(transition_system_input):
    # get transition system
    transys = TranSys(transition_system_input)
    return transys

def get_virtuals(transys, sys_aut, prod_aut):
    # get virtual graphs
    virtual_sys = sync_prod(transys, sys_aut)
    virtual = sync_prod(transys, prod_aut)
    return virtual, virtual_sys

def extract_test_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    init = [ast.literal_eval(s) for s in data['init']]
    goals = [ast.literal_eval(s) for s in data['goals']]
    labels = {ast.literal_eval(s): data['labels'][s] for s in data['labels'].keys()}
    sysformula = data['sysformula']
    testformula = data['testformula']
    type = data['type']
    # labels = data['labels']

    if 'states' in data:
        states = data['states']
        transitions = data['transitions']
    else:
        mazefile = data['mazefile']
        states, transitions = get_states_and_transitions_from_file(mazefile)

    return init, goals, labels, sysformula, testformula, states, transitions, type


def find_test_environment(filename):
    init, goals, labels, sysformula, testformula, states, transitions, type = extract_test_data(filename)
    # get transition_system_input from states and transitions
    transition_system_input = TransitionSystemInput(states,transitions,labels, init)

    # setup problem
    sys_aut, test_aut, prod_aut = get_automata(sysformula, testformula)
    transys = get_transition_system(transition_system_input)
    virtual, virtual_sys = get_virtuals(transys, sys_aut, prod_aut)

    # optimize
    d, flow = solve(virtual, transys, prod_aut, virtual_sys, case = type)

    # print output
    ncuts = 0
    for cut in d:
        if d[cut] > 0.9:
            ncuts+=1
            print('{0} to {1} at {2}'.format(cut[0], cut[1],d[cut]))

    return d, flow


def save_output(filename):
    pass

def main():
    parser = argparse.ArgumentParser(
        description="filename of json file to solve"
    )
    parser.add_argument("--filename", required=True, type=str)
    args = parser.parse_args()

    filename = args.filename
    d, flow = find_test_environment(filename)
