import plotly.offline as py
from plotly.graph_objs import *

import community
import networkx as nx
import colorlover as cl
import numpy as np
import pickle

py.init_notebook_mode(connected=True)

# This is your Facebook id. It can also be a number
CENTRAL_ID = 'kernelogy'

# This is the pickle file containing the raw graph data
GRAPH_FILENAME = 'friend_graph.pickle'
# To generate the friend graph, see:
# friend_graph a dict of lists in the form {'friend1': ['friend2, 'friend3']}
with open(GRAPH_FILENAME, 'rb') as f:
    friend_graph = pickle.load(f)
# First, we'll clean the edges of the grap
edges = []
nodes = [CENTRAL_ID]

# Only keep friends with at least 2 common friends
central_friends = {}

for k, v in friend_graph.items():
    # This contains the list number of mutual friends.
    # Doing len(v) does not work because ometimes instead of returning mutual
    # friends, Facebook returns all the person's friends
    intersection_size = len(np.intersect1d(list(friend_graph.keys()), v))
    if intersection_size > 2:
        central_friends[k] = v
        
print('Firtered out {} items'.format(len(friend_graph.keys()) - len(central_friends.keys())))

# Extract edges from graph
for k, v in central_friends.items():
    for item in v:
        if item in central_friends.keys() or item == CENTRAL_ID:
            edges.append((k, item))
# Create the graph. 
# Small reminder: friends are the nodes and friendships are the edges here
G = nx.Graph()
G.add_nodes_from([CENTRAL_ID])
G.add_nodes_from(central_friends.keys())

G.add_edges_from(edges)
print('Added {} edges'.format(len(edges) ))
pos = nx.spring_layout(G)
part = community.best_partition(G)

# Get a list of all node ids# Get a  
nodeID = G.node.keys()
# The louvain community library returns cluster ids, we have turn them into colors using color lovers

colors = cl.scales['12']['qual']['Paired']

def scatter_nodes(pos, labels=None, color='rgb(152, 0, 0)', size=8, opacity=1):
    # pos is the dict of node positions
    # labels is a list  of labels of len(pos), to be displayed when hovering the mouse over the nodes
    # color is the color for nodes. When it is set as None the Plotly default color is used
    # size is the size of the dots representing the nodes
    # opacity is a value between [0,1] defining the node color opacity

    trace = Scatter(x=[], 
                    y=[],  
                    mode='markers', 
                    marker=Marker(
        showscale=False,
        colorscale='Greens',
        reversescale=True,
        color=[], 
        size=10,
    line=dict(width=0)))
    for nd in nodeID:
        trace['x'].append(pos[nd][0])
        trace['y'].append(pos[nd][1])
        color = colors[part[nd] % len(colors)]
        trace['marker']['color'].append(color)
    attrib=dict(name='', text=labels , hoverinfo='text', opacity=opacity) # a dict of Plotly node attributes
    trace=dict(trace, **attrib)# concatenate the dict trace and attrib
    trace['marker']['size']=size

    return trace
def scatter_edges(G, pos, line_color='#a3a3c2', line_width=1, opacity=.2):
    trace = Scatter(x=[], 
                    y=[], 
                    mode='lines'
                   )
    for edge in G.edges():
        trace['x'] += [pos[edge[0]][0],pos[edge[1]][0], None]
        trace['y'] += [pos[edge[0]][1],pos[edge[1]][1], None]  
        trace['hoverinfo']='none'
        trace['line']['width']=line_width
        if line_color is not None: # when it is None a default Plotly color is used
            trace['line']['color']=line_color
    return trace   
# Node label information available on hover. Note that some html tags such as line break <br> are recognized within a string.
labels = []

for nd in nodeID:
      labels.append('{} ({})'.format(nd, part[nd],))
trace1 = scatter_edges(G, pos, line_width=0.25)
trace2 = scatter_nodes(pos, labels=labels)
width=1200
height=1200
axis=dict(showline=False, # hide axis line, grid, ticklabels and  title
          zeroline=False,
          showgrid=False,
          showticklabels=False,
          title='' 
          )
layout=Layout(title= '',
          
    font= Font(),
    showlegend=False,
    autosize=False,
    width=width,
    height=height,
    xaxis=dict(
        title='Facebook friend graph',
        titlefont=dict(
        size=14,
        color='#fff'),
        showgrid=False,
        
        showline=False,
        showticklabels=False,
        zeroline=False
    ),
    yaxis=YAxis(axis),
    margin=Margin(
        l=40,
        r=40,
        b=85,
        t=100,
        pad=0,
       
    ),
    hovermode='closest',
    paper_bgcolor='rgba(0,0,0,1)',
    plot_bgcolor='rgba(0,0,0,1)'
    )


data=Data([trace1, trace2])

fig = Figure(data=data, layout=layout)
# py.iplot(fig, image='png')
py.plot(fig, image='jpeg')

