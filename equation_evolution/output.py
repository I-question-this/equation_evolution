"""Output methods
"""
import matplotlib.pyplot as plt
import numpy as np


def plotEquationStructure(individual, output_name):
    nodes, edges, labels = gp.graph(individual)

    g = pgv.AGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    g.layout(prog="dot")

    for i in nodes:
        n = g.get_node(i)
        n.attr["label"] = labels[i]

    g.draw(output_name)


def plotTrojanCreation(benign, malware, piecewiseTrojan, evolvedTrojan, points, insertionStart, insertionStop, outputName):
    # Plot the lines
    plt.plot(points, [benign(x) for x in points], 'b--',
        label="Benign"
    )
    plt.plot(points, [malware(x) for x in points], 'g--',
        label="Malware"
    )
    plt.plot(points, [piecewiseTrojan(x) for x in points], 'k--',
        label="Piecewise Ideal"
    )
    plt.plot(points, [evolvedTrojan(x) for x in points], 'r',
        label="Evolved Trojan"
    )

    # Mark the insertion start and stop points
    plt.axvline(insertionStart)
    plt.axvline(insertionStop)

    # Make the legend
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2,
        mode="expand", borderaxespad=0.
    )
    # Save the figure
    plt.savefig(output_name)
    # Close the figure
    plt.close()


def plotTrojanRemoval(actualBenign, malware, evolvedTrojan, evolvedBenign, points, insertionStart, insertionStop, outputName):
    # Plot the lines
    plt.plot(points, [actualBenign(x) for x in points], 'b--',
        label="Actual Benign"
    )
    plt.plot(points, [malware(x) for x in points], 'g--',
        label="Malware"
    )
    plt.plot(points, [evolvedTrojan(x) for x in points], 'r--',
        label="Evolved Trojan"
    )
    plt.plot(points, [evolvedBenign(x) for x in points], 'k',
        label="Evolved Benign"
    )

    # Mark the insertion start and stop points
    plt.axvline(insertionStart)
    plt.axvline(insertionStop)

    # Make the legend
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2,
        mode="expand", borderaxespad=0.
    )
    # Save the figure
    plt.savefig(output_name)
    # Close the figure
    plt.close()



def writeEquation(individiual, output_name):
    with open(output_name, "w") as f:
        f.write(str(individiual))

