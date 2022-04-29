#!/usr/bin/env python
# coding: utf-8

# ### 根据布局好的子图以及子图间的结构拼合成为一张大图

# In[8]:


import os
import math
import json
import time
import config
import numpy as np
import networkx as nx
from tqdm import tqdm
from readgml import readgml
from networkx.utils import is_string_like


# In[2]:


def get_subgraph_r(path):
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
    return r_max


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
        yield indent+"]"
    yield "]"


# In[6]:


def subgraph_fatten():
    # 获取每个子图等效节点的实际半径，圆心坐标
    # 在前一步骤已经丢弃了部分非联通分量
    # 若不在set里的整数id则不是子图的等效节点, 这些节点是为了等效社区添加的辅助节点，ID从最大子图ID下一个开始
    subgraph_list_set = set([file.split('.')[0] for file in os.listdir(f'../temp/{config.DATASET}/subgraphs')])  
    
    nodes, edges = readgml.read_gml(f'../temp/{config.DATASET}/equivalence_structure_layouted/equivalence_structure.gml')
    
    T1 = time.perf_counter()
    subgraph2position, subgraph2r = {}, {}
    for node in nodes:
        if str(node['id']) in subgraph_list_set:
            x = node['x']
            y = node['y']
            subgraph2position[str(node['id'])] = [x, y]
            subgraph2r[str(node['id'])] = node['w']
    
    # 获取还原结构的比例，子图布局与节点大小不变，变换等效结构，如果不变换等效结构，缩放子图坐标，而不缩放节点大小，会使得节点发生重叠
    subgraph2acc_r = {}
    r_ratio = []
    for subgraph in subgraph2r:
        subgraph2acc_r[subgraph] = get_subgraph_r(f'../temp/{config.DATASET}/layouted_subgraphs/{subgraph}.gml')
        r_ratio.append(float(subgraph2acc_r[subgraph])/float(subgraph2r[subgraph]))
    stretch_factor = np.mean(r_ratio)
    # 根据等效结构拼合子图
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
    # 此段代码用于实际的应用当中，但由于此次代码的目的是为了跑实验，故先注释掉，节约跑代码的时间
    #==========================#
#     i = 0
#     G = nx.Graph()
#     for subgraph in subgraph2r:
#         nodes, edges = readgml.read_gml(f'../temp/{config.DATASET}/layouted_subgraphs/{subgraph}.gml')
#         for node in nodes:
#             node_id = str(node['id'])
#             whd = node['w']
#             color = color_list[i%11]
#             x = node['x'] + subgraph2position[str(subgraph)][0] * stretch_factor
#             y = node['y'] + subgraph2position[str(subgraph)][1] * stretch_factor
#             G.add_node(node_id, graphics = {'x':x,'y':y,'z':0,'w':whd,'h':whd,'d':whd,'fill':color}, L = '')
#         for edge in edges:
#             G.add_edge(str(edge['source']),str(edge['target']))
#         i += 1
    
#     if not os.path.exists(f'../temp/{config.DATASET}/fattened_large_graph_without_subgraph_edge'): # 保存子图之间不存在连边的拼合好的大图
#         os.makedirs(f'../temp/{config.DATASET}/fattened_large_graph_without_subgraph_edge')
#     # 这个gml用于直接出图，类似生成dblp那一类的大图，时间关系就不继续开发了，后续如果有需要就接着这个写，包括一些节点大小，节点颜色的设置
#     # 由于后续评估不需要，因此相关节点属性设置不再继续开发
#     # 输出两个大图文件，第一个是不包含子图之间连边的大图用于直接可视化，第二个是包含子图之间连边的大图用于后续和其他算法比较计算时间
#     with open(f'../temp/{config.DATASET}/fattened_large_graph_without_subgraph_edge/fattened_large_graph.gml', 'w') as fp:
#         for line in generate_gml(G):
#             line+='\n'
#             fp.write(line)
    #==========================#
    # 包含子图之间连边的大图用于后续和其他算法比较计算时间
    i = 0
    final_layout_json = {}  # VSAN以及Tulip的最终layout均用json存储与评估，且VSAN不再进行后期的微调操作
    final_layout_json['node_position'] = {} #用于存储最后节点的位置即二维空间的坐标
    final_layout_json['edges'] = [] # 用于存储图的连边，从而在后续的评估中计算图论距离
    node_set = set()
    G2Tulip = nx.Graph()
    for subgraph in subgraph2r:
        nodes, edges = readgml.read_gml(f'../temp/{config.DATASET}/layouted_subgraphs/{subgraph}.gml')
        for node in nodes:
            node_id = str(node['id'])
            G2Tulip.add_node(str(node_id))
            node_set.add(node_id)
            whd = node['w']
            color = color_list[i%11]
            # 这一块与上面直接出图对大图进行拼接不同，上面对等效结构的缩放会使得图结构超出gephi的方形区域，而此处使用对子图缩放，将图范围限制在可控范围内
            x = node['x']/stretch_factor + subgraph2position[str(subgraph)][0]
            y = node['y']/stretch_factor + subgraph2position[str(subgraph)][1]
            final_layout_json['node_position'][str(node_id)] = [x, y]
        i += 1
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    executed_time = json.load(open(f'../temp/{config.DATASET}/executed_time.json', 'r'))
    executed_time['subgraph_fatten'] = delta_t
    json.dump(executed_time, open(f'../temp/{config.DATASET}/executed_time.json', 'w'))

    G_original = nx.read_gml(f'../temp/{config.DATASET}/preprocessed_gml/graph.gml')
    for source, target in tqdm(G_original.edges):
        if str(source) in node_set and str(target) in node_set:
            final_layout_json['edges'].append([str(source),str(target)])
            G2Tulip.add_edge(str(source),str(target))
    
    if not os.path.exists(f'../temp/{config.DATASET}/final_layout_json_to_evaluation'): # 保存子图之间存在连边的拼合好的大图
        os.makedirs(f'../temp/{config.DATASET}/final_layout_json_to_evaluation')
    json.dump(final_layout_json, open(f'../temp/{config.DATASET}/final_layout_json_to_evaluation/vasn.json', 'w'))
    if not os.path.exists(f'../temp/{config.DATASET}/gml_to_tulip_layout'): # 保存子图之间存在连边的拼合好的大图
        os.makedirs(f'../temp/{config.DATASET}/gml_to_tulip_layout')
    nx.write_gml(G2Tulip, f'../temp/{config.DATASET}/gml_to_tulip_layout/graph.gml')


# In[9]:


if __name__ == '__main__':
    subgraph_fatten()

