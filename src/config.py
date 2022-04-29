DATASET = 'Slashdot0811'  # 数据集
SUBGRAPH_LAYOUTER = 'gephi-tool'  # 用gephi-tool与pyfa2进行布局，由于gephi-tool有方形限制，故对超大规模图进行布局时需要使用pyfa2
GEPHI_TOOL_PROCESS_NUM = 10  # 子图布局的进程数
EVALUATION_MAX_NODES = 3000  # 用于评估时的最大采样点数