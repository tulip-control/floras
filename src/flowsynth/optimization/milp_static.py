'''
Gurobipy implementation of the MILP for static obstacles.
'''
from gurobipy import GRB
import time
import numpy as np
from ipdb import set_trace as st
import networkx as nx
from src.flowsynth.optimization.utils import find_map_G_S
from gurobipy import *
from copy import deepcopy
import os
import json

# Callback function
def cb(model, where):
    if where == GRB.Callback.MIPNODE:
        # Get model objective
        obj = model.cbGet(GRB.Callback.MIPNODE_OBJBST) # Current best objective
        sol_count = model.cbGet(GRB.Callback.MIPNODE_SOLCNT) # No. of feasible solns found.

        # Has objective changed?
        if abs(obj - model._cur_obj) > 1e-8:
            # If so, update incumbent
            model._cur_obj = obj

        # Terminate if objective has not improved in 60s
        # Current objective is less than infinity.

        if sol_count >= 1:
            if time.time() - model._time > 60:
                model._data["term_condition"] = "Obj not changing"
                model.terminate()
        else:
            # Total termination time if the optimizer has not found anything in 5 min:
            if time.time() - model._time > 600:
                model._data["term_condition"] = "Timeout"
                model.terminate()

# Gurobi implementation
def solve_opt_static(GD, SD, callback="cb", logger=None, logger_runtime_dict=None):
    cleaned_intermed = [x for x in GD.acc_test if x not in GD.acc_sys]
    # create G and remove self-loops
    G = GD.graph
    to_remove = []
    for i, j in G.edges:
        if i == j:
            to_remove.append((i,j))
    G.remove_edges_from(to_remove)

    # remove intermediate nodes
    G_minus_I = deepcopy(G)
    G_minus_I.remove_nodes_from(cleaned_intermed)

    # create S and remove self-loops
    S = SD.graph
    to_remove = []
    for i, j in S.edges:
        if i == j:
            to_remove.append((i,j))
    S.remove_edges_from(to_remove)

    model_edges = list(G.edges)
    model_nodes = list(G.nodes)
    model_edges_without_I = list(G_minus_I.edges)
    model_nodes_without_I = list(G_minus_I.nodes)

    src = GD.init
    sink = GD.sink
    inter = cleaned_intermed

    # for the flow on S
    map_G_to_S = find_map_G_S(GD,SD)

    s_sink = SD.acc_sys
    s_src = SD.init[0]


    model_s_edges = list(S.edges)
    model_s_nodes = list(S.nodes)

    model = Model()
    # Define variables
    f = model.addVars(model_edges, name="flow")
    m = model.addVars(model_nodes_without_I, name="m")
    d = model.addVars(model_edges, vtype=GRB.BINARY, name="d")

    # Define Objective
    term = sum(f[i,j] for (i, j) in model_edges if i in src)
    ncuts = sum(d[i,j] for (i, j) in model_edges)
    reg = 1/len(model_edges)
    model.setObjective(term - reg*ncuts, GRB.MAXIMIZE)

    # Define constraints
    # Nonnegativity - lower bounds
    model.addConstrs((d[i, j] >= 0 for (i,j) in model_edges), name='d_nonneg')
    model.addConstrs((m[i] >= 0 for i in model_nodes_without_I), name='mu_nonneg')
    model.addConstrs((f[i, j] >= 0 for (i,j) in model_edges), name='f_nonneg')

    # upper bounds
    model.addConstrs((d[i, j] <= 1 for (i,j) in model_edges), name='d_upper_b')
    model.addConstrs((m[i] <= 1 for i in model_nodes_without_I), name='mu_upper_b')
    # capacity (upper bound for f)
    model.addConstrs((f[i, j] <= 1 for (i,j) in model_edges), name='capacity')

    # preserve flow of at least 1
    model.addConstr((1 <= sum(f[i,j] for (i, j) in model_edges if i in src)), name='conserve_F')

    # conservation
    model.addConstrs((sum(f[i,j] for (i,j) in model_edges if j == l) == sum(f[i,j] for (i,j) in model_edges if i == l) for l in model_nodes if l not in src and l not in sink), name='conservation')

    # no flow into source or out of sink
    model.addConstrs((f[i,j] == 0 for (i,j) in model_edges if j in src or i in sink), name="no_out_sink_in_src")

    # cut constraint (cut edges have zero flow)
    model.addConstrs((f[i,j] + d[i,j] <= 1 for (i,j) in model_edges), name='cut_cons')

    # source sink partitions
    for i in model_nodes_without_I:
        for j in model_nodes_without_I:
            if i in src and j in sink:
                model.addConstr(m[i] - m[j] >= 1)

    # max flow cut constraint (cut variable d partitions the groups)
    model.addConstrs((d[i,j] - m[i] + m[j] >= 0 for (i,j) in model_edges_without_I))

    # --------- map static obstacles to other edges in G
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in model_edges[count+1:]:
            if out_state == GD.node_dict[imap][0] and in_state == GD.node_dict[jmap][0]:
                model.addConstr(d[i, j] == d[imap, jmap])


    # ---------  add bidirectional cuts on G
    for count, (i,j) in enumerate(model_edges):
        out_state = GD.node_dict[i][0]
        in_state = GD.node_dict[j][0]
        for (imap,jmap) in model_edges[count+1:]:
            if in_state == GD.node_dict[imap][0] and out_state == GD.node_dict[jmap][0]:
                model.addConstr(d[i, j] == d[imap, jmap])

    # --------- set parameters
    # Last updated objective and time (for callback function)
    model._cur_obj = float('inf')
    model._time = time.time()
    model.Params.Seed = np.random.randint(0,100)

    # store model data for logging
    model._data = dict()
    model._data["term_condition"] = None

    # optimize
    if callback=="cb":
        t0 = time.time()
        model.optimize(callback=cb)
        tf = time.time()
        delt = tf - t0
    else:
        t0 = time.time()
        model.optimize()
        tf = time.time()
        delt = tf - t0

    model._data["runtime"] = model.Runtime
    model._data["flow"] = None
    model._data["ncuts"] = None

    # Storing problem variables:
    model._data["n_bin_vars"] = model.NumBinVars
    model._data["n_cont_vars"] = model.NumVars - model.NumBinVars
    model._data["n_constrs"] = model.NumConstrs

    f_vals = []
    d_vals = []
    flow = None
    exit_status = None

    if model.status == 4:
        model.Params.DualReductions = 0
        exit_status = 'inf'
        model._data["status"] = "inf/unbounded"
        return 0,0,exit_status
    elif model.status == 11 and model.SolCount < 1:
        exit_status = 'not solved'
        model._data["status"] = "not_solved"
        model._data["exit_status"] = exit_status
    elif model.status == 2 or (model.status == 11 and model.SolCount >= 1):
        if model.status == 2:
            model._data["status"] = "optimal"
            model._data["term_condition"] = "optimal found"
        else:
            # feasible. maybe be optimal.
            model._data["status"] = "feasible"

        # --------- parse output
        d_vals = dict()
        f_vals = dict()

        for (i,j) in model_edges:
            f_vals.update({(i,j): f[i,j].X})
        for (i,j) in model_edges:
            d_vals.update({(i,j): d[i,j].X})

        flow = sum(f[i,j].X for (i,j) in model_edges if i in src)
        model._data["flow"] = flow
        ncuts = 0

        for key in d_vals.keys():
            if d_vals[key] > 0.9:
                ncuts+=1
                print('{0} to {1} at {2}'.format(GD.node_dict[key[0]], GD.node_dict[key[1]],d_vals[key]))

        model._data["ncuts"] = ncuts
        exit_status = 'opt'
        model._data["exit_status"] = exit_status
    elif model.status == 3:
        exit_status = 'inf'
        model._data["status"] = "inf"
    else:
        st()

    if not os.path.exists("log"):
        os.makedirs("log")
    with open('log/opt_data.json', 'w') as fp:
        json.dump(model._data, fp)

    return d_vals, flow, exit_status
