"""Testing current code."""
import sys
sys.path.append('../')
from flowsynth.components.automata import get_system_automaton, get_tester_automaton, get_product_automaton
from flowsynth.components.transition_system import TransitionSystemInput, TranSys
from flowsynth.components.product import sync_prod
from flowsynth.optimization.optimize import solve


if __name__=='__main__':
    states_list = [0,1,2,3,4,5]
    transitions_dict = {0: [1,2,3], 1: [2,3,4], 2: [3,4,5], 3: [4], 4: [5,0], 5: [5]}
    labels_dict = {0 : ['a'], 5: ['goal'], 3: ['int']}
    init_list = [0]

    transition_system_input = TransitionSystemInput(states_list, transitions_dict, labels_dict, init_list)

    sys_formula = 'F(goal)'
    test_formula = 'F(int)'

    # get automata
    sys_aut, spot_aut_sys = get_system_automaton(sys_formula)
    test_aut, spot_aut_test = get_tester_automaton(test_formula)
    prod_aut = get_product_automaton(spot_aut_sys, spot_aut_test)

    # get transition system
    transys = TranSys(transition_system_input)

    # get virtual graphs
    virtual_sys = sync_prod(transys, sys_aut)
    virtual = sync_prod(transys, prod_aut)

    d, flow = solve(virtual, transys, prod_aut, virtual_sys, case = 'static')

    assert flow >= 1.0
