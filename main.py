#!/usr/bin/env python3

"""
Inspired by https://deap.readthedocs.io/en/master/tutorials/basic/part1.html
"""

import operator

from deap import base
from deap import creator
from deap import gp
from deap import tools

from equation_evolution.primatives import pset


# Type Creation
## Indvidual Defintions
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin,
               pset=pset)

# Tool registration
toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual,
                 toolbox.expr)

# Testing
ind1 = toolbox.individual()
nodes, edges, labels = gp.graph(ind1)

import pygraphviz as pgv

g = pgv.AGraph()
g.add_nodes_from(nodes)
g.add_edges_from(edges)
g.layout(prog="dot")

for i in nodes:
	n = g.get_node(i)
	n.attr["label"] = labels[i]

g.draw("tree.pdf")

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

g = nx.Graph()
g.add_nodes_from(nodes)
g.add_edges_from(edges)

nx.draw(g, pos = graphviz_layout(g), prog="dot")
plt.show()
