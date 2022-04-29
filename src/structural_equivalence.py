#!/usr/bin/env python
# coding: utf-8

# ### 统计所有边的数量，然后再在计算weight时进行统一的归一化，即不管图的规模如何，都得到统一边权范围的图

# ### 取等效结构的最大联通部分，那些与最大联通部分不连通的子图全部舍弃

# In[6]:


import os
import time
import math
import json
import config
import networkx as nx
from tqdm import tqdm
from readgml import readgml
from networkx.utils import is_string_like


# ### 需要写一个图位置中心化的函数，但不写中心化的函数，在子图布局近似为圆形的情况下影响不大

# In[2]:


def get_subgraph_inner_degree_and_r(path):
    # 获取子图内部连边的度（通过连边统计），以及布局之后的图半径，通过gml文件统计
    # 跟精细的处理是对图进行中心化，即通过图的上下左右节点的坐标，求出水平和竖直方向和坐标原点的位移，然后做平移即得到中心化的图
    nodes, edges = readgml.read_gml(path)
    r_max = 0
    for node in nodes:
        x = node['x']
        y = node['y']
        r = math.sqrt(x**2 + y**2)
        if r > r_max:
            r_max = r
    return 2*len(edges), r_max


# In[3]:


def generate_gml(G):
    # gml图生成器直接将networkx源代码进行修改
    # recursively make dicts into gml brackets
    def listify(d,indent,indentlevel):
        result='[ \n'
        for k,v in d.items():
            if type(v)==dict:
                v=listify(v,indent,indentlevel+1)
            result += (indentlevel+1)*indent +                 string_item(k,v,indentlevel*indent)+'\n'
        return result+indentlevel*indent+"]"

    def string_item(k,v,indent):
        # try to make a string of the data
        if type(v)==dict: 
            v=listify(v,indent,2)
        elif is_string_like(v):
            v='"%s"'%v
        elif type(v)==bool:
            v=int(v)
        return "%s %s"%(k,v)

    # check for attributes or assign empty dict
    if hasattr(G,'graph_attr'):
        graph_attr=G.graph_attr
    else:
        graph_attr={}
    if hasattr(G,'node_attr'):
        node_attr=G.node_attr
    else:
        node_attr={}

    indent=2*' '
    count=iter(range(len(G)))
    node_id={}

    yield "graph ["
    if G.is_directed():
        yield indent+"directed 1"
    # write graph attributes 
    for k,v in G.graph.items():
        if k == 'directed':
            continue
        yield indent+string_item(k,v,indent)
    # write nodes
    for n in G:
        yield indent+"node ["
        # get id or assign number
        #nid=G.node[n].get('id',next(count))
        #node_id[n]=nid
        nid = n
        node_id[n]=n
        # 上两行对原代码进行修改，以原始输入的id作为输出图文件的id
        yield 2*indent+"id %s"%nid
        label=G.node[n]['L']
        if is_string_like(label):
            label='"%s"'%label
        yield 2*indent+'label %s'%label
        if n in G:
          for k,v in G.node[n].items():
              if k=='id' or k == 'label' or k == 'L': continue
              yield 2*indent+string_item(k,v,indent)
        yield indent+"]"
    # write edges
    for u,v,edgedata in G.edges(data=True):
        source_color = G.node[u]['graphics']['fill']
        target_color = G.node[v]['graphics']['fill']
        yield indent+"edge ["
        yield 2*indent+"source %s"%u
        yield 2*indent+"target %s"%v
        yield 2*indent+"weight %s"%edgedata['weight']
        yield indent+"]"
    yield "]"


# In[4]:


def structural_equivalence():
    edges_not_in_same_subgraph_list = json.load(open(f'../temp/{config.DATASET}/edges_not_in_same_subgraph_list.json', 'r'))
    node2subgraph = json.load(open(f'../temp/{config.DATASET}/node2subgraph.json', 'r'))
    subgraph_list = set()
    for node in node2subgraph:
        subgraph_list.add(str(node2subgraph[node]))

    subgraph_list = list(subgraph_list)
    
    T1 = time.perf_counter()
    edge_num_between_subgraphs = {} # 不同子图之间的连边数
    for source, target in edges_not_in_same_subgraph_list:
        if f'{node2subgraph[str(source)]}|{node2subgraph[str(target)]}' not in edge_num_between_subgraphs:
            edge_num_between_subgraphs[f'{node2subgraph[str(source)]}|{node2subgraph[str(target)]}'] = 0
        edge_num_between_subgraphs[f'{node2subgraph[str(source)]}|{node2subgraph[str(target)]}'] += 1
    
    subgraph2out_degree = {} # 用于后续步骤边权的归一化
    for source, target in edges_not_in_same_subgraph_list:
        if node2subgraph[str(source)] not in subgraph2out_degree:
            subgraph2out_degree[str(node2subgraph[str(source)])] = 0
        subgraph2out_degree[str(node2subgraph[str(source)])] += 1
    # 获取归一化连边权重    
    G = nx.Graph()
    for subgraph in subgraph_list:
        G.add_node(str(subgraph), graphics = {'w':0,'h':0,'d':0,'fill':''}, L = '')
    iii = 0
    edge2weight = {} # 存储连边与归一化权重之间的关系
    # 做无向图处理
    weight_list = [] # 用于第二次归一化，将边的权重归一化到1-20之间，对应不同的图得到统一的
    # 连边权重，这样就可以用一个布局参数，后面通过自动缩放图结实现自适应拼接
    for i in tqdm(range(len(subgraph_list))):
        iii += 1
        for ii in range(len(subgraph_list) - iii):
            flag = 0
            if subgraph_list[i]+'|'+subgraph_list[ii+iii] in edge_num_between_subgraphs:
                weight_1 = edge_num_between_subgraphs[subgraph_list[i]+'|'+subgraph_list[ii+iii]] / subgraph2out_degree[subgraph_list[i]]  
                flag += 1
            else:
                weight_1 = 0
            if subgraph_list[ii+iii]+'|'+subgraph_list[i] in edge_num_between_subgraphs:
                weight_2 = edge_num_between_subgraphs[subgraph_list[ii+iii]+'|'+subgraph_list[i]] / subgraph2out_degree[subgraph_list[ii+iii]]
                flag += 1
            else:
                weight_2 = 0
            if flag > 0:
                edge2weight[f'{subgraph_list[i]}|{subgraph_list[ii + iii]}'] = weight_1 + weight_2
                weight_list.append(weight_1 + weight_2)
    max_weight = max(weight_list)
    min_weight = min(weight_list)
    # 对权重做线性变换，最大边权为20，最小为1
    a = 4/(max_weight-min_weight)
    b = 1-a*min_weight
    for edge in edge2weight:
        G.add_weighted_edges_from([(edge.split('|')[0], edge.split('|')[1], edge2weight[edge]*a+b)])
    # 设置等效节点的大小与颜色，并使用简单社区等效复杂社区
    subgraph2inner_degree = {}
    subgraph2r = {}
    # 用于做等比例缩放
    inner_degree_list = []
    r_list = []
    for subgraph in subgraph_list:
        inner_degree, r = get_subgraph_inner_degree_and_r(f'../temp/{config.DATASET}/layouted_subgraphs/{subgraph}.gml')
        inner_degree_list.append(inner_degree)
        r_list.append(r)
        subgraph2inner_degree[str(subgraph)] = inner_degree
        subgraph2r[str(subgraph)] = r
    r_max = max(r_list)
    inner_degree_ratio_max = max(inner_degree_list)
    r_ratio = 300/r_max
    inner_degree_ratio = 20/inner_degree_ratio_max
    color_list = [
        '#ff6666',
        '#0099cc',
        '#ffff66',
        '#ff9900',
        '#99cc33',
        '#cc6699',
        '#9933ff',
        '#33cc33',
        '#9966cc',
        '#ff33cc',
        '#009966'
    ]
    i = 0
    added_nodeID = len(subgraph_list)
    for subgraph in subgraph_list:
        G.node[subgraph]['graphics']['w'] = r_ratio * subgraph2r[subgraph]
        G.node[subgraph]['graphics']['h'] = r_ratio * subgraph2r[subgraph]
        G.node[subgraph]['graphics']['d'] = r_ratio * subgraph2r[subgraph]
        G.node[subgraph]['graphics']['fill'] = color_list[i%11]
        i += 1
        for edge in range(int(subgraph2inner_degree[subgraph]*inner_degree_ratio)):
            G.add_node(str(added_nodeID),graphics = {'w':2,'h':2,'d':2,'fill':'#666666'}, L = '')
            G.add_weighted_edges_from([(subgraph, str(added_nodeID), 200)])
            added_nodeID += 1
    # 去除不连通分量，大图相应的子图被去掉，子图中相应的节点即被去掉
    sub_G_list = nx.connected_component_subgraphs(G)
    max_node_num = 0
    for sub_G in sub_G_list:
        if len(sub_G.nodes) >= max_node_num:
            max_node_num = len(sub_G.nodes)
            selected_G = sub_G
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    executed_time = json.load(open(f'../temp/{config.DATASET}/executed_time.json', 'r'))
    executed_time['structural_equivalence'] = delta_t
    json.dump(executed_time, open(f'../temp/{config.DATASET}/executed_time.json', 'w'))
    if not os.path.exists(f'../temp/{config.DATASET}/equivalence_structure_to_layout'):
        os.makedirs(f'../temp/{config.DATASET}/equivalence_structure_to_layout')
    with open(f'../temp/{config.DATASET}/equivalence_structure_to_layout/equivalence_structure.gml', 'w') as fp:
        for line in generate_gml(selected_G):
            line+='\n'
            fp.write(line)


# In[5]:


if __name__ == '__main__':
    structural_equivalence()

