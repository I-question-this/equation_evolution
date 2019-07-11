#!/usr/bin/env python3
"""Runs the main program multiple times with different equations
"""
import argparse
import os
import subprocess

outputDirectory = "scriptedOutput"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

scriptOutputDirectory = "output"
trojanCreationPlotPath = "{}/TrojanCreation--halloffame-0--equation_results.png".format(scriptOutputDirectory)
trojanCreationEquationPath = "{}/TrojanCreation--halloffame-0--equation_written.txt".format(scriptOutputDirectory)
trojanRemovalPlotPath = "{}/TrojanRemoval--halloffame-0--equation_results.png".format(scriptOutputDirectory)
trojanRemovalEquationPath = "{}/TrojanRemoval--halloffame-0--equation_written.txt".format(scriptOutputDirectory)

equations = {
        "large1": "div(pow(sin(cos(sub(mul(pow(mul(sub(0.0, 1.0), pow(1.0, 0.0)), div(sub(x, x), pow(x, 0.0))), neg(div(div(1.0, x), add(0.0, 0.0)))), pow(mul(sub(cos(x), sin(-1.0)), sin(sin(x))), mul(div(add(-1.0, x), add(x, x)), mul(div(x, x), cos(0.0))))))), pow(sin(sub(sub(sub(neg(div(0.0, x)), sin(cos(1.0))), sin(neg(sin(-1.0)))), div(pow(add(mul(x, 1.0), sin(-1.0)), pow(div(x, 1.0), pow(x, 1.0))), add(sin(neg(x)), mul(cos(x), cos(x)))))), sin(sub(mul(neg(sin(sub(x, 0.0))), add(sub(sub(x, -1.0), sub(0.0, 1.0)), pow(neg(1.0), sin(-1.0)))), sub(pow(sin(cos(x)), add(sin(0.0), mul(0.0, x))), neg(div(pow(0.0, 0.0), sin(0.0)))))))), neg(sub(cos(cos(cos(sub(cos(div(x, x)), sub(div(-1.0, x), neg(1.0)))))), sin(sub(mul(sub(sin(neg(0.0)), sub(add(x, x), neg(x))), cos(div(mul(0.0, 0.0), add(1.0, x)))), sin(pow(sin(pow(x, 0.0)), add(sin(x), sub(x, -1.0)))))))))", 
        "large2": "div(sub(sin(div(add(mul(add(pow(-1.0, x), pow(x, x)), div(pow(1.0, 1.0), sub(x, x))), mul(sin(sin(x)), cos(sub(x, x)))), add(neg(cos(pow(x, x))), add(sin(div(1.0, x)), mul(div(1.0, 0.0), mul(x, 0.0)))))), sub(mul(cos(mul(add(sin(x), neg(x)), sub(sub(x, 1.0), neg(x)))), neg(sub(pow(sin(x), pow(0.0, x)), pow(pow(1.0, -1.0), add(0.0, x))))), cos(neg(sin(cos(div(-1.0, x))))))), add(pow(cos(cos(div(neg(cos(x)), cos(cos(1.0))))), sub(mul(cos(pow(mul(x, 0.0), pow(x, 1.0))), sin(pow(pow(x, x), pow(1.0, 0.0)))), neg(mul(mul(mul(x, 1.0), div(x, x)), sin(mul(x, x)))))), div(div(add(sub(cos(cos(-1.0)), mul(mul(-1.0, x), sub(x, -1.0))), sub(add(sub(x, 1.0), cos(1.0)), cos(neg(x)))), div(sin(neg(neg(1.0))), add(mul(mul(-1.0, x), neg(-1.0)), cos(sub(x, 1.0))))), cos(sin(neg(mul(sin(x), neg(x))))))))",
        "exponential1": "pow(add(1,1),x)",
        "exponential2": "pow(add(1,1),add(x,1))",
        "linear1": "x",
        "linear2": "add(x,1)",
        "polynomial1": "pow(x,1)",
        "polynomial2": "pow(x,add(1,1))",
        "reciprocal1": "div(1,x)",
        "reciprocal2": "div(add(1,1),x)",
        "root1": "pow(x,div(1,add(1,1)))",
        "root2": "pow(x,div(1,add(add(1,1),1)))",
        "sin1": "sin(x)",
        "sin2": "sin(add(x,1))",
        "cos1": "cos(x)",
        "cos2": "cos(add(x,1)"
}

numberOfGenerationsCreation = 2000
numberOfGenerationsRemoval = 2000

def runEvolution():
    for equation1Name, equation1 in equations.items():
        for equation2Name, equation2 in equations.items():
            if equation1Name == equation2Name:
                continue
            # Run evolving the Trojan
            subprocess.run(
                [
                    "./main.py",
                    equation1,
                    equation2,
                    "True",
                    "--verbose",
                    "--max_number_of_generations",
                    str(numberOfGenerationsCreation)
                ]
            )
            # Run devolving the Trojan
            subprocess.run(
                [
                    "./main.py",
                    equation2,
                    equation1,
                    "False",
                    "--verbose",
                    "--max_number_of_generations",
                    str(numberOfGenerationsRemoval)
                ]
            )
            # Save files
            os.rename(
                trojanCreationPlotPath,
                "{}/{}-{}--trojan_creation--equation_plot.png".format(
                    outputDirectory,
                    equation1Name,
                    equation2Name
                )
            )
            os.rename(
                trojanCreationEquationPath,
                "{}/{}-{}--trojan_creation--equation_written.txt".format(
                    outputDirectory,
                    equation1Name,
                    equation2Name
                )
            )
            os.rename(
                trojanRemovalPlotPath,
                "{}/{}-{}--trojan_removal--equation_plot.png".format(
                    outputDirectory,
                    equation1Name,
                    equation2Name
                )
            )
            os.rename(
                trojanRemovalEquationPath,
                "{}/{}-{}--trojan_removal--equation_written.txt".format(
                    outputDirectory,
                    equation1Name,
                    equation2Name
                )
            )


def produceLaTeXFigures():
    def getIdentifiers(fileName):
        fileName = fileName.split("--")
        equationNames = fileName[0].split("-")
        equation1 = equationNames[0]
        equation2 = equationNames[1]
        objective = fileName[1].split("_")[1]
        return equation1, equation2, objective

    plotFileNames = {}
    evolvedEquations = {}

    for subDir, dirs, files in os.walk(outputDirectory):
        for fileName in files:
            filePath = subDir + os.sep + fileName
            if filePath.endswith(".png"):
                identifiers = getIdentifiers(fileName)
                plotFileNames[identifiers] = fileName.split(".")[0]
            elif filePath.endswith(".txt"):
                identifiers = getIdentifiers(fileName)
                with open(filePath, "r") as fStream:
                    evolvedEquations[identifiers] = fStream.read().rstrip()

    def createLaTeXFigure(identifiers):
        figureCode = "\\begin{{figure}}[h!]\n\t\\centering\n\t\\includegraphics[height=0.6\\textheight,keepaspectratio]{{\"img/plots/{}\"}}\n\t\\caption{{\n\t\t{}\n\t}}\n\\end{{figure}}\n"
        plotFileName = plotFileNames[identifiers]
        evolvedEquation = evolvedEquations[identifiers]
        equation1 = equations[identifiers[0]]
        equation2 = equations[identifiers[1]]

        if identifiers[2] == "creation":
            caption = "\"{}\" inserted into \"{}\"".format(equation2, equation1)
        else:
            trojanEquation = evolvedEquations[(identifiers[0],identifiers[1],"creation")]
            caption = "Recreating \"{}\" by removing \"{}\" thus producing \"{}\""
            caption = caption.format(equation1, equation2, evolvedEquation)
        return figureCode.format(plotFileName, caption)

    texFile = ""
    for identifiers in plotFileNames.keys():
        with open(os.path.join(outputDirectory, "{}.tex".format("-".join(identifiers))), "w") as fileStream:
            fileStream.write(createLaTeXFigure(identifiers))


if __name__ == "__main__":
    def trueOrFalse(string:str):
        if string.lower() == "true":
            return True
        if string.lower() == "false":
            return False
        raise ValueError("Must be 'True' or 'False'")

    parser = argparse.ArgumentParser()
    parser.add_argument("--runEvolution", type=trueOrFalse, default=True,
            help="Rather to run the evolution or not. Default is True"
        )

    args = parser.parse_args()

    if args.runEvolution:
        runEvolution()

    produceLaTeXFigures()

