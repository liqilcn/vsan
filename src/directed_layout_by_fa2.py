#!/usr/bin/env python
# coding: utf-8

# In[14]:


import os
import time
import json
import config
from readgml import readgml


# ### 直接用fa2进行布局

# In[19]:


def directed_layout_by_fa2():
    gen_code_cmd = 'python3 ../gephi-tool/scripts/gen_code.py ../gephi-tool/subgraph_layout_config.json'
    os.system(gen_code_cmd)
    print('Code generation finish!')
    if not os.path.exists(f'../temp/{config.DATASET}/directed_layouted_by_fa2'): os.makedirs(f'../temp/{config.DATASET}/directed_layouted_by_fa2')
    gephi_tool_abs_path = os.path.abspath('../gephi-tool/scripts/run.py') # 重新配置gephi-tool之后只需更改这一行
    source_abs_path = os.path.abspath(f'../temp/{config.DATASET}/preprocessed_gml')
    target_abs_path = os.path.abspath(f'../temp/{config.DATASET}/directed_layouted_by_fa2')
    layout_cmd = f"python {gephi_tool_abs_path} {source_abs_path} {target_abs_path} {1}"
    T1 = time.perf_counter()
    os.system(layout_cmd)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    executed_time = {}
    executed_time['layout'] = delta_t
    json.dump(executed_time, open(f'../temp/{config.DATASET}/fa2_executed_time.json', 'w'))
    print('layout finish!')
    
    nodes, edges = readgml.read_gml(f'../temp/{config.DATASET}/directed_layouted_by_fa2/graph.gml')
    final_layout_json = {}
    final_layout_json['node_position'] = {}
    final_layout_json['edges'] = []
    for node in nodes:
        node_id = str(node['id'])
        x = node['x']
        y = node['y']
        final_layout_json['node_position'][node_id] = [x, y]
    for edge in edges:
        final_layout_json['edges'].append([str(edge['source']), str(edge['target'])])
    if not os.path.exists(f'../temp/{config.DATASET}/final_layout_json_to_evaluation'): # 保存子图之间存在连边的拼合好的大图
        os.makedirs(f'../temp/{config.DATASET}/final_layout_json_to_evaluation')
    json.dump(final_layout_json, open(f'../temp/{config.DATASET}/final_layout_json_to_evaluation/fa2.json', 'w'))


# In[18]:


if __name__ == "__main__":
    directed_layout_by_fa2()

