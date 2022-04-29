#!/usr/bin/env python
# coding: utf-8

# In[7]:


import config
from subgraph_segmentation import *
from graph_layout import *
from structural_equivalence import *
from subgraph_fatten import *
from directed_layout_by_fa2 import directed_layout_by_fa2
from evaluation_layout import final_evaluation


# In[8]:


def vsan():
    # 1. 先对大图进行划分
    if config.DATASET == 'DBLP':
        segmentation_by_venue()
    else:
        segmentation_by_louvain()
    # 2. 使用图布局工具对子图进行布局
    subgraph_layout_by_gephi_tool()
    # 3. 对大图的结构进行等效
    structural_equivalence()
    print('eq finished!')
    # 4. 对等效结构进行布局
    equivalence_structure_layout_by_gephi_tool()
    print('eq layout finished!')
    # 5. 拼合成为大图
    subgraph_fatten()
    print('fatten finished!')


# In[9]:


if __name__ == '__main__':
    vsan()
    # directed_layout_by_fa2()
    # final_evaluation()