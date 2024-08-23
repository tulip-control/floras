import spot
import pdb
from ast import literal_eval as make_tuple
import matplotlib.pyplot as plt
from collections import OrderedDict as od
import networkx as nx
import os
from ipdb import set_trace as st

class TransitionSystemInput():
    """Input format containing data to create a transition system."""
    def __init__(self,states,transitions,labels, init):
        self.states = states
        self.transitions = transitions
        self.labels = labels
        self.init = init
        self.next_state_dict = None
        self.setup()

    def setup(self):
        self.next_state_dict = self.transitions

class TranSys():
    """Transition system class.
    T = (S, A, delta, S_init, AP, L).
    S: states
    A: actions
    delta: transition relation,
    S_init: initial_states,
    AP: the set of atomic propositions,
    L: labels.

    Args:
    S, A, E, I, AP_dict
    """
    def __init__(self, transition_system_input = None, S=None, A=None, E=None, I=None, AP_dict=None):
        self.S = S
        self.A = A
        self.E = E
        self.I = I
        self.AP_dict = AP_dict
        self.Sigma=None
        self.AP = None
        self.L = None
        self.G = None
        self.input = transition_system_input
        if self.input:
            self.setup()

    def setup(self):
        self.S = list(self.input.states)
        self.A = ['act'+str(k) for k in range(0,5)] # update for different actions later
        self.construct_transition_function()
        self.get_APs()
        self.construct_initial_conditions()
        self.construct_labels()


    def print_transitions(self):
        for e_out, e_in in self.E.items():
            print("node out: " + str(e_out) +  " node in: " + str(e_in))

    def construct_transition_function(self):
        self.E = dict()
        for s in self.input.states:
            i = 0
            for ns in self.input.transitions[s]:
                self.E[(s, 'act'+str(i))] = ns
                i += 1

    def get_APs(self):
        """
        Set of atomic propositions required to define a specification.
        Need not initialize all cells of the grid as APs, only
        the relevant states to define what the agent must do.
        Need to setup atomic propositions.
        """
        # self.AP = [spot.formula.ap("goal"), spot.formula.ap("int")]
        self.AP_dict = od()
        for s in self.S: # If the system state is the init or goal
            self.AP_dict[s] = []
            if s in self.input.labels:
                labels = self.input.labels[s]
                for label in labels:
                    self.AP_dict[s].append(spot.formula.ap(label))

    def construct_initial_conditions(self):
        self.I = self.input.init

    def construct_labels(self):
        self.L = od()
        for s in self.S:
            if s in self.AP_dict.keys():
                self.L[s] = set(self.AP_dict[s])
            else:
                self.L[s] = {}

    def save_plot(self, fn):
        self.G = nx.DiGraph()
        self.G.add_nodes_from(list(self.S))

        edges = []
        edge_attr = dict()
        node_attr = dict()
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            act = state_act[1]
            edge = (out_node, in_node)
            edge_attr[edge] = {"act": act}
            edges.append(edge)
        self.G.add_edges_from(edges)
        nx.set_edge_attributes(self.G, edge_attr)

        """Plot the product transition system as dot graph."""
        G_agr = nx.nx_agraph.to_agraph(self.G)
        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            ntuple = make_tuple(n)
            n.attr['fillcolor'] = 'white'
            n.attr['shape'] = 'circle'

        if not os.path.exists("imgs"):
            os.makedirs("imgs")
        G_agr.draw("imgs/"+fn+".pdf",prog='dot')
