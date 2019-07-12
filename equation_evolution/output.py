"""Output methods
"""
import matplotlib.pyplot as plt
import numpy as np

# def createLaTeXFigure(identifiers):
    # figureCode = "\\begin{{figure}}[h!]\n\t\\centering\n\t\\includegraphics[height=0.6\\textheight,keepaspectratio]{{\"img/plots/{}\"}}\n\t\\caption{{\n\t\t{}\n\t}}\n\\end{{figure}}\n"
    # plotFileName = plotFileNames[identifiers]
    # evolvedEquation = evolvedEquations[identifiers]
    # equation1 = equations[identifiers[0]]
    # equation2 = equations[identifiers[1]]

    # if identifiers[2] == "creation":
        # caption = "\"{}\" inserted into \"{}\"".format(equation2, equation1)
    # else:
        # trojanEquation = evolvedEquations[(identifiers[0],identifiers[1],"creation")]
        # caption = "Recreating \"{}\" by removing \"{}\" thus producing \"{}\""
        # caption = caption.format(equation1, equation2, evolvedEquation)
    # return figureCode.format(plotFileName, caption)

# texFile = ""
# for identifiers in plotFileNames.keys():
    # with open(os.path.join(outputDirectory, "{}.tex".format("-".join(identifiers))), "w") as fileStream:
        # fileStream.write(createLaTeXFigure(identifiers))


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
    plt.savefig(outputName)
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
    plt.savefig(outputName)
    # Close the figure
    plt.close()



def writeEquation(individiual, output_name):
    with open(output_name, "w") as f:
        f.write(str(individiual))

