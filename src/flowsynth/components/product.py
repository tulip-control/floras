"""Contains Product class for virtual product graph and virtual system graph."""
import sys
sys.path.append("..")
import spot
from matplotlib import pyplot as plt
from ipdb import set_trace as st
from collections import OrderedDict as od
import os
import networkx as nx
from itertools import product
from src.flowsynth.components.transition_system import TranSys
from src.flowsynth.components.automata import Automaton

spot.setup(show_default='.tvb')

class Product(TranSys):
    def __init__(self, product_transys, spec_prod_automaton):
        super().__init__()
        self.transys=product_transys
        self.automaton=spec_prod_automaton
        self.G_initial = None
        self.G = None
        self.S = list(product(product_transys.S, spec_prod_automaton.Q))
        self.Sdict = od()
        self.reverse_Sdict = od()
        for k in range(len(self.S)):
            self.Sdict[self.S[k]] = "s"+str(k)
            self.reverse_Sdict["s"+str(k)] = self.S[k]
        self.A = product_transys.A
        self.I = [(init, spec_prod_automaton.qinit) for init in product_transys.I]
        self.AP = spec_prod_automaton.Q

    def print_transitions(self):
        for e_out, e_in in self.E.items():
            print("node out: " + str(e_out) +  " node in: " + str(e_in))

    def pruned_sync_prod(self):
        self.construct_labels()
        self.E = dict()
        aut_state_edges = [(si[0], sj) for si, sj in self.automaton.delta.items()]

        nodes_to_add = []
        s0 = self.transys.I[0]
        q0 = self.automaton.qinit
        nodes_to_add.append((s0, q0))
        nodes_to_keep = []
        nodes_to_keep.append((s0, q0))

        while len(nodes_to_add) > 0:
            next_nodes = []
            for (s,q) in nodes_to_add:
                for a in self.transys.A:
                    if (s,a) in list(self.transys.E.keys()):
                        t = self.transys.E[(s,a)]
                        for p in self.automaton.Q:
                            if (q,p) in aut_state_edges:
                                label = self.transys.L[t]
                                if self.automaton.get_transition(q, label) == p:
                                    self.E[((s,q), a)] = (t,p)
                                    if (t,p) not in nodes_to_keep:
                                        nodes_to_keep.append((t,p))
                                        next_nodes.append((t,p))
            nodes_to_add = next_nodes

        self.S = nodes_to_keep
        self.G_initial = nx.DiGraph()
        nodes = []
        for node in self.S:
            nodes.append(self.Sdict[node])
        self.G_initial.add_nodes_from(nodes)
        edges = []
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            act = state_act[1]
            s_out = self.Sdict[out_node]
            s_in = self.Sdict[in_node]
            edges.append((s_out, s_in))
        self.G_initial.add_edges_from(edges)
        self.identify_SIT()
        self.to_graph()

    def construct_labels(self):
        self.L = od()
        for s in self.S:
            self.L[s] = s[1]

    def identify_SIT(self):
        self.src = [s for s in self.I]
        try:
            self.int = [s for s in self.S if s[1] in self.automaton.Acc["test"]]
        except:
            self.int=[]
        self.sink = [s for s in self.S if s[1] in self.automaton.Acc["sys"]]

    def process_nodes(self, node_list):
        for node in node_list:
            node_st = self.Sdict[node]
            if node in self.sink and node not in self.int:
                if node_st not in self.plt_sink_only:
                    self.plt_sink_only.append(node_st)

            if node in self.int and node not in self.sink:
                if node_st not in self.plt_int_only:
                    self.plt_int_only.append(node_st)

            if node in self.int and node in self.sink:
                if node_st not in self.plt_sink_int:
                    self.plt_sink_int.append(node_st)

            if node in self.src:
                self.plt_src.append(node_st)

    def to_graph(self):
        self.G = nx.DiGraph()
        self.G.add_nodes_from(list(self.Sdict.values()))
        self.plt_sink_only = [] # Finding relevant nodes connected to graph with edges
        self.plt_int_only= []
        self.plt_sink_int = []
        self.plt_src = []
        edges = []
        edge_attr = dict()
        node_attr = dict()
        for state_act, in_node in self.E.items():
            out_node = state_act[0]
            act = state_act[1]
            edge = (self.Sdict[out_node], self.Sdict[in_node])
            edge_attr[edge] = {"act": act}
            edges.append(edge)
            self.process_nodes([out_node, in_node])
        self.G.add_edges_from(edges)
        nx.set_edge_attributes(self.G, edge_attr)

    def base_dot_graph(self, graph=None):
        if graph == None:
            st()
            G_agr = nx.nx_agraph.to_agraph(self.G)
        else:
            G_agr = nx.nx_agraph.to_agraph(graph)

        G_agr.node_attr['style'] = 'filled'
        G_agr.node_attr['gradientangle'] = 90

        for i in G_agr.nodes():
            n = G_agr.get_node(i)
            node = self.reverse_Sdict[n]
            n.attr['shape'] = 'circle'
            if n in self.plt_sink_only:
                n.attr['fillcolor'] = '#ffb000'
            elif n in self.plt_int_only:
                n.attr['fillcolor'] = '#648fff'
            elif n in self.plt_sink_int:
                n.attr['fillcolor'] = '#ffb000'
            elif n in self.plt_src:
                n.attr['fillcolor'] = '#dc267f'
            else:
                n.attr['fillcolor'] = '#ffffff'
            n.attr['label']= ''
        return G_agr

    def save_plot(self, fn):
        G_agr = self.base_dot_graph(graph=self.G_initial)
        if not os.path.exists("imgs"):
            os.makedirs("imgs")
        G_agr.draw("imgs/"+fn+".pdf",prog='dot')

def sync_prod(system, aut):
    prod = Product(system, aut)
    prod.pruned_sync_prod()
    return prod
