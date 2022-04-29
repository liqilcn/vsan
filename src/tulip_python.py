# Powered by Python 3.9
# To cancel the modifications performed by the script
# on the current graph, click on the undo button.
# Some useful keyboard shortcuts:
#   * Ctrl + D: comment selected lines.
#   * Ctrl + Shift + D: uncomment selected lines.
#   * Ctrl + I: indent selected lines.
#   * Ctrl + Shift + I: unindent selected lines.
#   * Ctrl + Return: run script.
#   * Ctrl + F: find selected text.
#   * Ctrl + R: replace selected text.
#   * Ctrl + Space: show auto-completion dialog.
from tulip import tlp
import time
import json
# The updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views
# The pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the
# "Run script " button.
# The runGraphScript(scriptFile, graph) function can be called to launch
# another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call
# (in the form [a-zA-Z0-9_]+.py)
# The main(graph) function must be defined
# to run the script on the current graph
DATASET = 'Nature'

def layout2evaluation_json(graph, layout_method):
    viewLayout = graph.getLayoutProperty("viewLayout")
    final_layout_json = {}  # VSAN以及Tulip的最终layout均用json存储与评估，且VSAN不再进行后期的微调操作
    final_layout_json['edges'] = [] # 用于存储图的连边，从而在后续的评估中计算图论距离
    node_id2position = {}
    for n in graph.getNodes():
        coordinate = viewLayout[n]
        node_id2position[str(n.id)] = [coordinate.getX(), coordinate.getY()]
    final_layout_json['node_position'] = node_id2position
    edge_list = []
    for e in graph.getEdges():
        source_node_id = graph.ends(e)[0].id
        target_node_id = graph.ends(e)[1].id
        edge_list.append([str(source_node_id), str(target_node_id)])
    final_layout_json['edges'] = edge_list
    json.dump(final_layout_json, open(f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/final_layout_json_to_evaluation/{layout_method}.json', 'w'))

def main(graph):
    
    ##fm3
    params = tlp.getDefaultPluginParameters('GML')
    params['filename'] = f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/gml_to_tulip_layout/graph.gml'
    graph = tlp.importGraph('GML', params)
    params = tlp.getDefaultPluginParameters('FM^3 (OGDF)', graph)
    tulip_executed_time = {}
    T1 = time.perf_counter()
    success = graph.applyLayoutAlgorithm('FM^3 (OGDF)', params)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    tulip_executed_time['fm3'] = delta_t
    layout2evaluation_json(graph, 'fm3')
    json.dump(tulip_executed_time, open(f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/tulip_executed_time.json', 'w'))
    print('fm3 finished!')
    
    ##PMDS
    params = tlp.getDefaultPluginParameters('GML')
    params['filename'] = f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/gml_to_tulip_layout/graph.gml'
    graph = tlp.importGraph('GML', params)
    params = tlp.getDefaultPluginParameters('Pivot MDS (OGDF)', graph)
    T1 = time.perf_counter()
    success = graph.applyLayoutAlgorithm('Pivot MDS (OGDF)', params)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    tulip_executed_time['pmds'] = delta_t
    layout2evaluation_json(graph, 'pmds')
    json.dump(tulip_executed_time, open(f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/tulip_executed_time.json', 'w'))
    print('pmds finished!')
    
    ##GRIP
    params = tlp.getDefaultPluginParameters('GML')
    params['filename'] = f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/gml_to_tulip_layout/graph.gml'
    graph = tlp.importGraph('GML', params)
    params = tlp.getDefaultPluginParameters('GRIP', graph)
    T1 = time.perf_counter()
    success = graph.applyLayoutAlgorithm('GRIP', params)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    tulip_executed_time['grip'] = delta_t
    layout2evaluation_json(graph, 'grip')
    json.dump(tulip_executed_time, open(f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/tulip_executed_time.json', 'w'))
    print('grip finished!')
    
    ##FR
    params = tlp.getDefaultPluginParameters('GML')
    params['filename'] = f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/gml_to_tulip_layout/graph.gml'
    graph = tlp.importGraph('GML', params)
    params = tlp.getDefaultPluginParameters('Fruchterman Reingold (OGDF)', graph)
    T1 = time.perf_counter()
    success = graph.applyLayoutAlgorithm('Fruchterman Reingold (OGDF)', params)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    tulip_executed_time['fr'] = delta_t
    layout2evaluation_json(graph, 'fr')
    json.dump(tulip_executed_time, open(f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/tulip_executed_time.json', 'w'))
    print('fr finished!')
    
    ##KK
    params = tlp.getDefaultPluginParameters('GML')
    params['filename'] = f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/gml_to_tulip_layout/graph.gml'
    graph = tlp.importGraph('GML', params)
    params = tlp.getDefaultPluginParameters('Kamada Kawai (OGDF)', graph)
    T1 = time.perf_counter()
    success = graph.applyLayoutAlgorithm('Kamada Kawai (OGDF)', params)
    T2 = time.perf_counter()
    delta_t = (T2 - T1)*1000
    tulip_executed_time['kk'] = delta_t
    layout2evaluation_json(graph, 'kk')
    print('kk finished!')
    
    
    json.dump(tulip_executed_time, open(f'/Users/liqi/Documents/macbook/jupyter_notebook/vsan_test/temp/{DATASET}/tulip_executed_time.json', 'w'))
  
