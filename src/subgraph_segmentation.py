#!/usr/bin/env python
# coding: utf-8

# In[10]:


import os
import json
import time
import config
import community
import networkx as nx
from networkx.utils import is_string_like
from tqdm import tqdm


# In[11]:


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
        label=G.node[n].get('L', str(nid))
#         node_json = G.node[n]['JSON']
        if is_string_like(label):
            label='"%s"'%label
        yield 2*indent+'label %s'%label
#         yield 2*indent+'json %s'%node_json
        if n in G:
          for k,v in G.node[n].items():
              if k=='id' or k == 'label' or k == 'L' or k == 'JSON': continue
              yield 2*indent+string_item(k,v,indent)
        yield indent+"]"
    # write edges
    for u,v,edgedata in G.edges(data=True):
#         source_color = G.node[u]['graphics']['fill']
#         target_color = G.node[v]['graphics']['fill']
        yield indent+"edge ["
        yield 2*indent+"source %s"%u
        yield 2*indent+"target %s"%v
#         yield 2*indent+"value 1.0"
#         # yield 2*indent+"color "+ get_edge_color_by_mixe_node_color(source_color, target_color)
#         yield 2*indent+"color #000000"
#         yield 2*indent+"path "+edge2path[str(u)+'|'+str(v)]
        yield indent+"]"
    yield "]"


# In[12]:


def segmentation_by_louvain():
    # 输出，子图GML，社区间连边的json，节点所属的子图类别
    if not os.path.exists(f'../temp/{config.DATASET}/subgraphs'): os.makedirs(f'../temp/{config.DATASET}/subgraphs')
    G = nx.read_gml(f'../temp/{config.DATASET}/preprocessed_gml/graph.gml')
    T1 = time.perf_counter()
    partition = community.best_partition(G)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    executed_time = {}
    executed_time['segmentation'] = delta_t
    json.dump(executed_time, open(f'../temp/{config.DATASET}/executed_time.json', 'w'))
    node2subgraph = {str(node):partition[node] for node in partition}
    # 获取每个社区（子图）对应的节点
    community2nodes = {}
    for node in partition:
        if partition[node] not in community2nodes:
            community2nodes[partition[node]] = []
        community2nodes[partition[node]].append(node)
    # 获取每个社区（子图）内部的连边
    community2edges = {}
    edges_not_in_same_subgraph_list = []
    for source, target in tqdm(G.edges):
        if partition[source] == partition[target]:
            if partition[source] not in community2edges:
                community2edges[partition[source]] = []
            community2edges[partition[source]].append((source, target))
        else:
            edges_not_in_same_subgraph_list.append([source, target])
    for cm in tqdm(community2nodes):
        G_tmp = nx.Graph()
        for node in community2nodes[cm]:
            G_tmp.add_node(str(node))
        if cm in community2edges:
            for source, target in community2edges[cm]:
                G_tmp.add_edge(str(source), str(target))
        with open(f'../temp/{config.DATASET}/subgraphs/{cm}.gml', 'w') as fp:
            for line in generate_gml(G_tmp):
                line+='\n'
                fp.write(line)
    json.dump(edges_not_in_same_subgraph_list, open(f'../temp/{config.DATASET}/edges_not_in_same_subgraph_list.json', 'w'))
    json.dump(node2subgraph, open(f'../temp/{config.DATASET}/node2subgraph.json', 'w'))


# In[13]:


def segmentation_by_venue():
    # 只针对DBLP数据集，其已有期刊或者会议的分类
    if not os.path.exists(f'../temp/{config.DATASET}/subgraphs'): os.makedirs(f'../temp/{config.DATASET}/subgraphs')
    G = nx.read_gml(f'../temp/{config.DATASET}/preprocessed_gml/graph.gml')
    pid2cluster = json.load(open(f'../temp/{config.DATASET}/preprocessed_gml/pid2cluster.json', 'r'))
    T1 = time.perf_counter()
    cluster2index = {}
    i = 0
    for pid in pid2cluster:
        cluster = pid2cluster[pid]
        if cluster not in cluster2index:
            cluster2index[cluster] = i
            i += 1
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    executed_time = {}
    executed_time['segmentation'] = delta_t
    json.dump(executed_time, open(f'../temp/{config.DATASET}/executed_time.json', 'w'))
    partition = {str(pid):str(cluster2index[pid2cluster[pid]]) for pid in pid2cluster}
    node2subgraph = {str(node):partition[node] for node in partition}
    # 获取每个社区（子图）对应的节点
    community2nodes = {}
    for node in partition:
        if partition[node] not in community2nodes:
            community2nodes[partition[node]] = []
        community2nodes[partition[node]].append(node)
    # 获取每个社区（子图）内部的连边
    community2edges = {}
    edges_not_in_same_subgraph_list = []
    for source, target in tqdm(G.edges):
        if partition[source] == partition[target]:
            if partition[source] not in community2edges:
                community2edges[partition[source]] = []
            community2edges[partition[source]].append((source, target))
        else:
            edges_not_in_same_subgraph_list.append([source, target])

    for cm in tqdm(community2nodes):
        G_tmp = nx.Graph()
        for node in community2nodes[cm]:
            G_tmp.add_node(str(node))
        if cm in community2edges:
            for source, target in community2edges[cm]:
                G_tmp.add_edge(str(source), str(target))
        with open(f'../temp/{config.DATASET}/subgraphs/{cm}.gml', 'w') as fp:
            for line in generate_gml(G_tmp):
                line+='\n'
                fp.write(line)
    json.dump(edges_not_in_same_subgraph_list, open(f'../temp/{config.DATASET}/edges_not_in_same_subgraph_list.json', 'w'))
    json.dump(node2subgraph, open(f'../temp/{config.DATASET}/node2subgraph.json', 'w'))


# In[ ]:


if __name__ == "__main__":
    segmentation_by_louvain()

