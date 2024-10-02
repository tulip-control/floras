def find_map_G_S(GD,SD):
    G_truncated = {}
    S_annot = {}
    map_G_to_S = {}
    for node in GD.node_dict:
        G_truncated.update({node: GD.node_dict[node][0]})
    for node in SD.node_dict:
        S_annot.update({node: SD.node_dict[node][0]})
    for node in G_truncated:
        sys_node_list = []
        for sys_node in S_annot:
            if G_truncated[node]  == S_annot[sys_node]:
                sys_node_list.append(sys_node)
        map_G_to_S.update({node: sys_node_list})

    return map_G_to_S
