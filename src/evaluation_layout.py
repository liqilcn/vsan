#!/usr/bin/env python
# coding: utf-8

# #### 给定一个包含节点坐标的GML，计算Jaccard similarity评估图布局的质量

# ### ref paper：Graph Layouts by t-SNE

# In[1]:


import os
import json
import random
import config
from readgml import readgml
from tqdm import tqdm


# In[2]:


def evaluate_layout_from_json(json_path):
    final_layout_json = json.load(open(json_path, 'r'))
    node_position = final_layout_json['node_position']
    edges = final_layout_json['edges']
    all_node_id2position = {}
    all_node_ids = []
    for node_id in node_position:
        all_node_ids.append(str(node_id))
        x = float(node_position[node_id][0])
        y = float(node_position[node_id][1])
        all_node_id2position[node_id] = (x, y)
    
    node2neigh = {}
    for edge in edges:
        source, target = edge[0], edge[1]
        if str(source) not in node2neigh:
            node2neigh[str(source)] = set()
        node2neigh[str(source)].add(str(target))
        if str(target) not in node2neigh:
            node2neigh[str(target)] = set()
        node2neigh[str(target)].add(str(source))
        
    if len(all_node_ids) <= config.EVALUATION_MAX_NODES:
        evaluated_nodes = all_node_ids
    else:
        evaluated_nodes = random.sample(all_node_ids, k=config.EVALUATION_MAX_NODES)
    
    valid_nodes = 0 # 图论的二阶邻居不为0的节点个数
    jaccard_similarity_sum = 0
    for node_id in tqdm(evaluated_nodes):
        # 获取该节点在图论意义上的所有二阶邻居
        neigh2_set = node2neigh[str(node_id)] # 目前是一阶
        for n_id in neigh2_set: # 从一阶邻居的邻居中再找一阶
            neigh2_set = neigh2_set|node2neigh[str(n_id)]
        neigh2_set_len = len(neigh2_set)  # 确定图论二阶邻居集合中节点的个数
        if neigh2_set_len == 0:
            continue
        
        x, y = all_node_id2position[node_id]
        node_id2dis = {}
        for node_id2 in all_node_id2position:
            x1, y1 = all_node_id2position[node_id2]
            dis = (x1-x)**2+(y1-y)**2  #开不开根号无所谓
            node_id2dis[node_id2] = dis
        node_id2dis_tuple = sorted(node_id2dis.items(), key = lambda item:item[1])
        k_nearest_nodes_set = set([str(node_id2dis_tuple[i][0]) for i in range(neigh2_set_len)])
        jaccard_similarity_sum += len(neigh2_set&k_nearest_nodes_set) / len(neigh2_set|k_nearest_nodes_set)
        valid_nodes += 1
    return jaccard_similarity_sum/valid_nodes


# In[3]:


def final_evaluation():
    files = os.listdir(f'../temp/{config.DATASET}/final_layout_json_to_evaluation')
    method2evaluation = {}
    for file in files:
        json_path = f'../temp/{config.DATASET}/final_layout_json_to_evaluation/{file}'
        perfor = evaluate_layout_from_json(json_path)
        method2evaluation[file.split('.')[0]] = format(perfor, '.4f')
    json.dump(method2evaluation, open(f'../temp/{config.DATASET}/evaluation_result.json', 'w'))


# In[6]:


if __name__ == "__main__":
    final_evaluation()

