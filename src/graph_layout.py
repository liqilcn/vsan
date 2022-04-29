#!/usr/bin/env python
# coding: utf-8

# ### 使用gephi-tool或者pyfa2对子图，等效结构，拼接后的大图进行布局

# In[7]:


import os
import time
import json
import config


# In[8]:


def subgraph_layout_by_gephi_tool():
    gen_code_cmd = 'python3 ../gephi-tool/scripts/gen_code.py ../gephi-tool/subgraph_layout_config.json'
    os.system(gen_code_cmd)
    print('Code generation finish!')
    if not os.path.exists(f'../temp/{config.DATASET}/layouted_subgraphs'): os.makedirs(f'../temp/{config.DATASET}/layouted_subgraphs')
    gephi_tool_abs_path = os.path.abspath('../gephi-tool/scripts/run.py') # 重新配置gephi-tool之后只需更改这一行
    source_abs_path = os.path.abspath(f'../temp/{config.DATASET}/subgraphs')
    target_abs_path = os.path.abspath(f'../temp/{config.DATASET}/layouted_subgraphs')
    layout_cmd = f"python {gephi_tool_abs_path} {source_abs_path} {target_abs_path} {config.GEPHI_TOOL_PROCESS_NUM}"
    T1 = time.perf_counter()
    os.system(layout_cmd)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    executed_time = json.load(open(f'../temp/{config.DATASET}/executed_time.json', 'r'))
    executed_time['subgraph_layout'] = delta_t
    json.dump(executed_time, open(f'../temp/{config.DATASET}/executed_time.json', 'w'))
    print('Subgraphs layout finish!')


# In[9]:


def equivalence_structure_layout_by_gephi_tool():
    # 使用gephi对等效好的大图结构进行布局
    gen_code_cmd = 'python3 ../gephi-tool/scripts/gen_code.py ../gephi-tool/equivalence_structure_layout_config.json'
    os.system(gen_code_cmd)
    print('Code generation finish!')
    if not os.path.exists(f'../temp/{config.DATASET}/equivalence_structure_layouted'): os.makedirs(f'../temp/{config.DATASET}/equivalence_structure_layouted')
    gephi_tool_abs_path = os.path.abspath('../gephi-tool/scripts/run.py') # 重新配置gephi-tool之后只需更改这一行
    source_abs_path = os.path.abspath(f'../temp/{config.DATASET}/equivalence_structure_to_layout/equivalence_structure.gml')
    target_abs_path = os.path.abspath(f'../temp/{config.DATASET}/equivalence_structure_layouted/equivalence_structure.gml')
    layout_cmd = f"python {gephi_tool_abs_path} {source_abs_path} {target_abs_path}"
    T1 = time.perf_counter()
    os.system(layout_cmd)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    executed_time = json.load(open(f'../temp/{config.DATASET}/executed_time.json', 'r'))
    executed_time['equivalence_structure_layout'] = delta_t
    json.dump(executed_time, open(f'../temp/{config.DATASET}/executed_time.json', 'w'))
    print('Equivalence Structure layout finish!')


# In[4]:


if __name__ == '__main__':
    subgraph_layout_by_gephi_tool()
    # equivalence_structure_layout_by_gephi_tool()

