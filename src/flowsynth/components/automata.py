"""
Contains automaton class and functions to set up automata from the specifications.
"""
from __future__ import annotations
import numpy as np
import spot
import networkx as nx
from collections import OrderedDict as od
import re
import os
from flowsynth.components.utils import powerset, neg, conjunction, disjunction


class Automaton:
    """
    Automaton class defines an Automaton as the tuple
    B = (Q, Sigma, Delta, Q_init, Acc)

    Args:
        Q: the states,
        q_init: the initial states,
        ap: the atomic propositions,
        delta: the transition function,
        Acc: The set of acceptance conditions.
    """
    def __init__(self, Q, qinit, ap, delta, Acc):
        self.Q=Q
        self.qinit = qinit
        self.delta = delta
        self.ap = ap # Must be a list
        self.Sigma = powerset(ap)
        self.Acc = Acc

    def print_transitions(self):
        """
        Print the transitions.
        """
        for k, v in self.delta.items():
            print("out state and formula: ", k, " in state: ", v)

    def complement_negation(self, propositions):
        """
        Negation of all atomic propositions not listed in propositions.

        Args:
            propositions: List of all propositions.
        """
        and_prop = spot.formula.And(list(propositions))
        comp_prop = [] # Complementary propositions
        for k in range(len(self.ap)):
            try:
                if not spot.contains(self.ap[k], and_prop):
                    comp_prop.append(spot.formula.Not(self.ap[k]))
            except:
                pdb.set_trace()
        and_comp_prop = spot.formula.And(comp_prop)
        complete_formula = spot.formula.And([and_prop, and_comp_prop]) # Taking complement of complete formula
        return complete_formula

    def get_transition(self, q0, propositions):
        """
        Get the transition.

        Args:
            q0: Initial state,
            propositions: List of propositions.
        """
        and_prop = spot.formula.And(list(propositions))
        transition = None
        for k,v in self.delta.items():
            if k[0] == q0:
                complete_formula = self.complement_negation(propositions)
                try:
                    if k[1] == True:
                        transition = v
                        return transition
                    if spot.contains(k[1], complete_formula):
                        transition = v
                        return transition
                except:
                    pdb.set_trace()
        return None

    def save_plot(self, fn):
        '''
        Save the an image of the automaton as a pdf.

        Args:
            fn: Name of the file to save the figure.
        '''
        G = nx.DiGraph()
        G.add_nodes_from(self.Q)
        edges = []
        for state_act, in_node in self.delta.items():
            out_node = state_act[0]
            act = state_act[1]
            edge = (out_node, in_node)
            edges.append(edge)
        G.add_edges_from(edges)

        G_agr = nx.nx_agraph.to_agraph(G)
        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            n.attr['shape'] = 'circle'
            n.attr['fillcolor'] = '#ffffff' # default color white
            # n.attr['label'] = ''
            try:
                if n in list(self.Acc["sys"]) and n not in list(self.Acc["test"]):
                    n.attr['fillcolor'] = '#ffb000' #yellow
            except:
                pass
            try:
                if n in list(self.Acc["sys"]):
                    n.attr['fillcolor'] = '#ffb000' #yellow
            except:
                pass

            try:
                if n in list(self.Acc["test"]) and n not in list(self.Acc["sys"]):
                    n.attr['fillcolor'] = '#648fff' # blue
            except:
                pass
            try:
                if n in list(self.Acc["test"]):
                    n.attr['fillcolor'] = '#648fff' # blue
            except:
                pass
            try:
                if n in list(self.Acc["test"]) and n in list(self.Acc["sys"]):
                    n.attr['fillcolor'] = '#ffb000' #yellow
            except:
                pass
        if not os.path.exists("imgs"):
            os.makedirs("imgs")
        G_agr.draw("imgs/"+fn+"_aut.pdf",prog='dot')

# Functions to take in spot formulas and return automaton object attributes:
def get_automaton(formula_str, playername):
    """
    Get automaton from LTL formula.

    Args:
        formula_str: LTL formula.
        playername: Whether the automaton is for the system ('sys') or the tester ('test').
    """
    spot_aut = spot.translate(formula_str, 'Buchi', 'state-based', 'complete')
    Q, qinit, tau, AP = construct_automaton_attr(spot_aut)
    Acc = construct_Acc(spot_aut, player=playername)
    aut = Automaton(Q, qinit, AP, tau, Acc)
    return aut, spot_aut

def get_system_automaton(formula_str):
    """
    Get system automaton from LTL formula.

    Args:
        formula_str: LTL formula.

    Returns:
        aut_sys: System automaton.
        spot_aut_sys: Spot system automaton.
    """
    playername="sys"
    aut_sys, spot_aut_sys= get_automaton(formula_str, playername)
    return aut_sys, spot_aut_sys

def get_tester_automaton(formula_str):
    """
    Get tester automaton from LTL formula.

    Args:
        formula_str: LTL formula.

    Returns:
        aut_test: Tester automaton.
        spot_aut_test: Spot tester automaton.
    """
    playername="test"
    aut_test, spot_aut_test = get_automaton(formula_str, playername)
    return aut_test, spot_aut_test

def get_product_automaton(spot_aut_sys, spot_aut_test):
    """
    Get the specification product automaton.

    Args:
        spot_aut_sys: Spot object of system automaton.
        spot_aut_test: Spot object of tester automaton.

    Returns:
        aut_prod: Specification product automaton.
    """
    spot_aut_prod = spot.product(spot_aut_sys, spot_aut_test)

    Q_prod, qinit_prod, tau_prod, AP_prod = construct_automaton_attr(spot_aut_prod)
    Acc_prod = construct_product_Acc(spot_aut_sys, spot_aut_test)

    aut_prod = Automaton(Q_prod, qinit_prod, AP_prod, tau_prod, Acc_prod)
    return aut_prod

def construct_Acc(spot_aut, player="sys"):
    '''
    Constructing the Automaton attribute Acc for a single automaton

    Args:
        spot_aut: Spot automaton.
        player: Player name, 'sys' or 'test'.

    Returns:
        Acc: Accepting states of the automaton.
    '''
    Acc = dict()
    acc_states = get_acc_states(spot_aut)
    acc_states_str = [get_state_str(state) for state in acc_states]
    Acc.update({player: acc_states_str})
    return Acc

# Functions to construct the product automaton
def get_prod_automaton(system_formula_str, tester_formula_str):
    """
    Construct the specification product automaton.

    Args:
        system_formula_str: LTL formula of system objective.
        tester_formula_str: LTL formula of test objective.

    Returns:
        aut_prod: Specification product automaton.
    """
    spot_aut_sys = spot.translate(system_formula_str, 'Buchi', 'state-based', 'complete')
    spot_aut_test = spot.translate(tester_formula_str, 'Buchi', 'state-based', 'complete')
    spot_aut_prod = spot.product(spot_aut_sys, spot_aut_test)

    Q_prod, qinit_prod, tau_prod, AP_prod = construct_automaton_attr(spot_aut_prod)
    Acc_prod = construct_product_Acc(spot_aut_sys, spot_aut_test)

    aut_prod = Automaton(Q_prod, qinit_prod, AP_prod, tau_prod, Acc_prod)
    return aut_prod

def construct_automaton_attr(spot_aut):
    '''
    Function that returns attributes (except accepting conditions) needed to build an Automaton object from a spot automaton.

    Args:
        spot_aut: Spot automaton.

    Returns:
        Q: states,
        qinit: initial states,
        tau: transitions,
        AP: atomic propositions.
    '''
    nstates = count_automaton_states(spot_aut)
    Q = [get_state_str(k) for k in range(nstates)]
    qinit = get_initial_state(spot_aut)
    tau = get_transitions(spot_aut)

    AP = get_APs(spot_aut)
    return Q, qinit, tau, AP

def count_automaton_states(spot_aut):
    '''
    Args:
        spot_aut: Spot automaton

    Returns:
        nstates: Number of states in the automaton
    '''
    hoa_body = get_hoa_body(spot_aut)
    nstates = 0
    for line in hoa_body:
        if 'State:' in line:
            nstates += 1
    return nstates

def get_hoa_body(spot_aut):
    """
    Parse the body of a hoa string.

    Args:
        spot_aut: Spot automaton

    Returns:
        hoa_body: Body of hoa string between the --BODY-- and --END-- lines
    """
    spot_aut_str = spot_aut.to_str('hoa')
    lines = spot_aut_str.split('\n')
    body_line = lines.index("--BODY--")
    end_line = lines.index("--END--")
    hoa_body = [lines[k] for k in range(len(lines)) if k > body_line and k < end_line]
    return hoa_body

def get_state_str(state):
    return "q"+str(state)

def read_state(state):
    '''
    Converting string state to an interger
    '''
    return int(state)

def get_initial_state(spot_aut):
    """
    Find the initial state.

    Args:
        spot_aut: Spot automaton

    Returns:
        init_state: Initial state of the automaton.
    """
    spot_aut_str = spot_aut.to_str('hoa')
    lines = spot_aut_str.split('\n')
    for line in lines:
        if 'Start:' in line:
            init_state=read_state(line.split()[1])
            assert isinstance(init_state, int)
            break
    init_state = get_state_str(init_state)
    return init_state

def get_transitions(spot_aut):
    """
    Get the transitions from the automaton.

    Args:
        spot_aut: Spot automaton

    Returns:
        tau: Transitions in the automaton
    """
    formula_dict = get_formula_dict(spot_aut)
    hoa = get_hoa_body(spot_aut)
    tau = {}
    for line in hoa:
        if 'State:' in line:
            out_state=line.split()[1]
            qout_st = get_state_str(out_state)
        else:
            cnf_str, qin_st, transition_acc_conditions = parse_hoa_transition_str(line)
            formula = parse_cnf_str(cnf_str, formula_dict)
            tau[(qout_st, formula)] = qin_st
    return tau

def get_formula_dict(spot_aut):
    '''
    Get formula dict from a list of spot atomic propositions.
    Formula dict is necessary for interpreting the atomic propositions.

    Args:
        spot_aut: Spot automaton

    Returns:
        formula_dict: Dictionary used in the automaton.
    '''
    AP = get_APs(spot_aut)
    formula_dict = {"t": True}
    num_AP = len(AP)
    for k in range(num_AP):
        formula_dict.update({str(k): AP[k]}) # Adding: {"k": AP[k]}
        formula_dict.update({"!"+str(k): neg(AP[k])}) # Adding: {"!k": neg(AP[k])}
    return formula_dict

def parse_hoa_transition_str(line):
    '''
    Function separating the hoa line into the cnf_portion, the incoming state, and
    any information on the accepting condition

    Args:
        line: Line with transition formula, input state, and transition acceptance as a string

    Returns:
        cnf_str: CNF formula,
        qin_st: Incoming state string,
        transition_acc_conditions: List of accepting conditions (if any)
    '''
    assert "[" in line
    assert "]" in line
    transition_acc_conditions = None # Default

    # CNF formula embedded within the first occurence of [ and the last occurence of ]
    cnf_str = line[line.find("[")+1: line.rfind("]")]

    # The rest of the string contains information on the incoming state, as well as any accepting
    # condition properties of that state.
    in_state_and_transition_acc = line[line.rfind("]")+1 :].split()
    in_state = read_state(in_state_and_transition_acc[0])
    qin_st = get_state_str(in_state)

    # See if there are any accepting conditions to catch:
    if len(in_state_and_transition_acc) > 1:
        transition_acc_conditions = in_state_and_transition_acc[1:]
    return cnf_str, qin_st, transition_acc_conditions

def parse_cnf_str(cnf_str, formula_dict):
    '''
    Unpacking a string cnf formula into a list of conjunctive formulas, and then parsing each of those
    conjunctive formulas separately.

    Args:
        cnf_str: CNF formula
        formula_dict: Dictionary used in the automaton

    Returns:
        formula: Parsed formula
    '''
    conj_str_list = [x.strip() for x in re.split(r"\|", cnf_str)]

    # If no disjunctions, parse the conjunctive string into spot and return
    if len(conj_str_list) == 1:
        formula = parse_conjunction_str(conj_str_list[0], formula_dict)
    else:
        conj_formula_list = []
        for conj_str in conj_str_list:
            conj_formula = parse_conjunction_str(conj_str, formula_dict)
            conj_formula_list.append(conj_formula)
        formula = disjunction(conj_formula_list)
    return formula

def parse_conjunction_str(conj_str, formula_dict):
    """
    Args:
        conj_str: String of cunjunctive formulas
        formula_dict: Formulas used in automaton

    Returns:
        formula: Formula in Spot form
    """
    spot_prop_list = []
    prop_list = re.split(r"[\[&\]]", conj_str)
    prop_list = list(filter(None, prop_list))
    for prop_str in prop_list:
        spot_prop_list.append(formula_dict[prop_str])
    if len(spot_prop_list) > 1:
        formula = conjunction(spot_prop_list)
    else:
        formula = spot_prop_list[0]
    return formula

def get_APs(spot_aut):
    '''
    Return a list of spot atomic propositions in a Spot Buchi automaton.

    Args:
        spot_aut: Spot automaton.

    Returns:
        AP: Atomic propositions used in automaton.
    '''
    spot_aut_str = spot_aut.to_str('hoa')
    lines = spot_aut_str.split('\n')
    AP = []
    for line in lines:
        if 'AP:' in line:
            parse_line = line.split()[1:]
            num_AP = int(parse_line[0])

            for k in range(1, len(parse_line)):
                ap_str = re.findall(r'"(.*?)"', parse_line[k])[0]
                assert isinstance(ap_str, str)

                # "Construct spot AP"
                ap = spot.formula.ap(ap_str)
                AP.append(ap)
            break
    return AP

def construct_product_Acc(spot_aut_sys, spot_aut_test):
    '''
    Return the accepting state dictionary for the synchronous product of the system and tester acceptances.

    Args:
        spot_aut_sys: Spot system automaton
        spot_aut_test: Spot test automaton

    Returns:
        Acc: Dictionary of accepting states for 'sys' and 'test'
    '''
    Acc = dict()
    spec_prod = spot.product(spot_aut_sys, spot_aut_test)

    sys_prod_acc_states_str = []
    test_prod_acc_states_str = []

    # Individual accepting states
    sys_acc_states = get_acc_states(spot_aut_sys)
    test_acc_states = get_acc_states(spot_aut_test)

    # Product state dictionary and list:
    product_states, product_states_dict = get_product_states(spec_prod)

    # Matching the definition in the paper of how the acceptance conditions are tracked:
    for pair in product_states:
        if pair[0] in sys_acc_states:
            prod_st = product_states_dict[pair]
            prod_st_str = get_state_str(prod_st)
            sys_prod_acc_states_str.append(prod_st_str)

        if pair[1] in test_acc_states:
            prod_st = product_states_dict[pair]
            prod_st_str = get_state_str(prod_st)
            test_prod_acc_states_str.append(prod_st_str)

    assert sys_prod_acc_states_str != [] # Not empty sanity check
    Acc.update({"sys": sys_prod_acc_states_str})

    assert test_prod_acc_states_str != [] # Not empty sanity check
    Acc.update({"test": test_prod_acc_states_str})
    return Acc

def get_product_states(spec_prod):
    '''
    Args:
        spec_prod: Specification product automaton.

    Returns:
        product_states: list of pairs of states (product_states[num_prod_state] = pair_prod_state)
        product_states_dict: dictionary of product state pairs mapping to a state number (product_states_dict[pair_prod_state] = num_prod_state)
    '''
    product_states = spec_prod.get_product_states()
    assert len(product_states) == count_automaton_states(spec_prod)
    product_states_dict = od()
    for k,prod in enumerate(product_states):
        product_states_dict.update({prod: k})
    return product_states, product_states_dict

def get_acc_states(spot_aut):
    '''
    Return a list of accepting states in the spot_automaton by parsing the body of the automaton
    In the prefix of the hoa_string, the succeeding portion of Acc refers to the number of accepting
    conditions in the automaton.

    Args:
        spot_aut: Spot automaton

    Returns:
        acc_states: Accepting states of the automaton.
    '''
    acc_states = []
    hoa_body = get_hoa_body(spot_aut)
    for line in hoa_body:
        if 'State:' in line:
            parse_line = line.split()
            state = parse_line[1]
            if len(parse_line) > 2:
                " If an acceptance condition is specified; might not be the best way"
                acc_states.append(read_state(state))
    assert acc_states != [] # Check that the algorithm worked.
    return acc_states
