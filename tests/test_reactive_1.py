"""Testing current code in reactive setup."""
import pytest

import sys
sys.path.append('../')
from src.flowsynth.components.automata import get_system_automaton, get_tester_automaton, get_product_automaton
from src.flowsynth.components.transition_system import TransitionSystemInput, TranSys
from src.flowsynth.components.product import sync_prod
from src.flowsynth.optimization.optimize import solve

def test_reactive():
    states_list = ['init', 'd1', 'd2', 'int_goal', 'p1', 'p2', 'goal']
    transitions_dict = {'init': ['d1','d2'], 'd1': ['d2','int_goal'], 'd2': ['d1', 'int_goal'],'int_goal': ['p1', 'p2'], 'p1': ['p2','goal'], 'p2': ['p1','goal'], 'goal': []}
    labels_dict = {'d1': ['door_1'], 'd2': ['door_2'], 'p1': ['door_1'], 'p2': ['door_2'], 'int_goal': ['beaver'], 'goal': ['goal']}
    init_list = ['init']

    transition_system_input = TransitionSystemInput(states_list, transitions_dict, labels_dict, init_list)

    sys_formula = 'F(beaver & F(goal))'
    test_formula = 'F(door_1) & F(door_2)'

    # get automata
    sys_aut, spot_aut_sys = get_system_automaton(sys_formula)
    test_aut, spot_aut_test = get_tester_automaton(test_formula)
    prod_aut = get_product_automaton(spot_aut_sys, spot_aut_test)

    # get transition system
    transys = TranSys(transition_system_input)
    transys.save_plot('reactive_plot')

    # get virtual graphs
    virtual_sys = sync_prod(transys, sys_aut)
    virtual = sync_prod(transys, prod_aut)
    virtual_sys.save_plot('virtual_sys')
    virtual.save_plot('virtual')


    d, flow = solve(virtual, transys, prod_aut, virtual_sys, case = 'reactive')

    assert flow >= 1.0

if __name__ == '__main__':
    test_reactive()
