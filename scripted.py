#!/usr/bin/env python3
"""Runs the main program multiple times with different equations
"""
import argparse
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import re
import subprocess
from deap import creator, gp
from functools import partial
from equation_evolution.output import plotTrojanCreation, plotTrojanRemoval
from equation_evolution.setup import creatorSetup, toolboxDirectSetup, toolboxGaussianSetup

outputDirectory = "output"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

equations = {
        "large1": "div(pow(sin(cos(sub(mul(pow(mul(sub(0.0, 1.0), pow(1.0, 0.0)), div(sub(x, x), pow(x, 0.0))), neg(div(div(1.0, x), add(0.0, 0.0)))), pow(mul(sub(cos(x), sin(-1.0)), sin(sin(x))), mul(div(add(-1.0, x), add(x, x)), mul(div(x, x), cos(0.0))))))), pow(sin(sub(sub(sub(neg(div(0.0, x)), sin(cos(1.0))), sin(neg(sin(-1.0)))), div(pow(add(mul(x, 1.0), sin(-1.0)), pow(div(x, 1.0), pow(x, 1.0))), add(sin(neg(x)), mul(cos(x), cos(x)))))), sin(sub(mul(neg(sin(sub(x, 0.0))), add(sub(sub(x, -1.0), sub(0.0, 1.0)), pow(neg(1.0), sin(-1.0)))), sub(pow(sin(cos(x)), add(sin(0.0), mul(0.0, x))), neg(div(pow(0.0, 0.0), sin(0.0)))))))), neg(sub(cos(cos(cos(sub(cos(div(x, x)), sub(div(-1.0, x), neg(1.0)))))), sin(sub(mul(sub(sin(neg(0.0)), sub(add(x, x), neg(x))), cos(div(mul(0.0, 0.0), add(1.0, x)))), sin(pow(sin(pow(x, 0.0)), add(sin(x), sub(x, -1.0)))))))))", 
        "large2": "div(sub(sin(div(add(mul(add(pow(-1.0, x), pow(x, x)), div(pow(1.0, 1.0), sub(x, x))), mul(sin(sin(x)), cos(sub(x, x)))), add(neg(cos(pow(x, x))), add(sin(div(1.0, x)), mul(div(1.0, 0.0), mul(x, 0.0)))))), sub(mul(cos(mul(add(sin(x), neg(x)), sub(sub(x, 1.0), neg(x)))), neg(sub(pow(sin(x), pow(0.0, x)), pow(pow(1.0, -1.0), add(0.0, x))))), cos(neg(sin(cos(div(-1.0, x))))))), add(pow(cos(cos(div(neg(cos(x)), cos(cos(1.0))))), sub(mul(cos(pow(mul(x, 0.0), pow(x, 1.0))), sin(pow(pow(x, x), pow(1.0, 0.0)))), neg(mul(mul(mul(x, 1.0), div(x, x)), sin(mul(x, x)))))), div(div(add(sub(cos(cos(-1.0)), mul(mul(-1.0, x), sub(x, -1.0))), sub(add(sub(x, 1.0), cos(1.0)), cos(neg(x)))), div(sin(neg(neg(1.0))), add(mul(mul(-1.0, x), neg(-1.0)), cos(sub(x, 1.0))))), cos(sin(neg(mul(sin(x), neg(x))))))))",
        "large3": "add(sub(add(x, cos(0.0)), mul(sub(add(sin(sin(0.0)), mul(x, pow(add(x, 1.0), pow(div(mul(neg(cos(sub(x, x))), 0.0), 0.0), cos(div(1.0, -1.0)))))), sin(div(x, cos(x)))), div(sub(cos(neg(sub(0.0, 0.0))), pow(add(cos(x), neg(-1.0)), -1.0)), x))), div(cos(x), pow(pow(sin(1.0), pow(mul(x, pow(cos(mul(x, x)), cos(cos(add(0.0, sub(sin(mul(-1.0, mul(0.0, 1.0))), add(x, -1.0))))))), div(mul(sin(x), mul(0.0, x)), cos(div(x, 0.0))))), add(cos(cos(add(add(x, neg(sin(pow(mul(add(add(sin(x), cos(add(cos(x), mul(x, x)))), x), mul(sin(x), x)), x)))), x))), div(div(div(mul(cos(0.0), sub(cos(sub(0.0, cos(add(x, sin(mul(1.0, x)))))), div(add(cos(sub(cos(x), cos(sin(div(1.0, x))))), cos(x)), sin(neg(x))))), x), pow(x, mul(add(sub(mul(add(sin(x), add(sin(div(x, x)), add(mul(pow(x, mul(x, x)), div(x, x)), 1.0))), pow(sub(x, sub(0.0, x)), mul(sub(x, cos(mul(x, x))), add(pow(x, sub(pow(x, 0.0), mul(-1.0, x))), neg(mul(-1.0, sub(1.0, 0.0))))))), div(div(add(cos(x), sub(1.0, x)), cos(cos(neg(0.0)))), sub(sub(x, cos(1.0)), mul(x, x)))), cos(div(x, -1.0))), sub(neg(neg(add(x, sin(-1.0)))), cos(x))))), x)))))",
        "exponential1": "pow(add(1,1),x)",
        "exponential2": "pow(add(1,1),add(x,1))",
        "exponential3": "pow(add(1,add(1,1)),add(x,add(1,1)))",
        "linear1": "x",
        "linear2": "add(x,1)",
        "linear3": "add(mul(add(1,add(1,1)),x),add(1,1))",
        "polynomial1": "pow(x,add(1,1))",
        "polynomial2": "pow(x,add(1,add(1,1)))",
        "polynomial3": "add(pow(x,add(1,add(1,1))),mul(add(1,1),pow(x,add(1,1))))",
        "reciprocal1": "div(1,x)",
        "reciprocal2": "div(add(1,1),x)",
        "reciprocal3": "sub(div(add(1,1),x),add(1,add(1,add(1,1))))",
        "root1": "pow(x,div(1,add(1,1)))",
        "root2": "pow(x,div(1,add(add(1,1),1)))",
        "root3": "pow(mul(add(1,1),x),div(1,add(add(1,1),1)))",
        "sin1": "sin(x)",
        "sin2": "sin(add(x,1))",
        "sin3": "mul(add(1,add(1,1)),sin(add(x,1)))",
        "cos1": "cos(x)",
        "cos2": "cos(add(x,1))",
        "cos3": "mul(add(1,add(1,1)),cos(add(x,1)))"
}


def runEvolution():
    for benignEquationName, benignEquation in equations.items():
        for malwareEquationName, malwareEquation in equations.items():
            if benignEquationName == malwareEquationName:
                continue
            for insertionStart, insertionStop in [(-2,2),(-1.5,1.5),(-1,1), (-0.5,0.5), (-0.25,0.25), (0,1), (-1,0), (-2,0),(0,2)]:
                outputName = os.path.join(outputDirectory,
                        "{}-{}-{}-{}.pickle".format(
                            benignEquationName,
                            malwareEquationName,
                            insertionStart,
                            insertionStop
                            )
                        )
                # Run evolving the Trojan
                programArgs = [
                                  "./main.py",
                                  benignEquation,
                                  benignEquationName,
                                  malwareEquation,
                                  malwareEquationName,
                                  "--output_name",
                                  outputName,
                                  "--verbose",
                                  "--max_number_of_generations",
                                  str(args.max_number_of_generations),
                                  "--insertion_start",
                                  str(insertionStart),
                                  "--insertion_stop",
                                  str(insertionStop),
                              ]
                if os.path.exists(outputName):
                    if not args.redo_removal:
                      # This simulation has already been run, 
                      # and we don't want to redo the removal portion
                      # so skip it
                      continue
                    else:
                      programArgs.extend(["--redoRemovalPickle", outputName])

                if args.special_removal:
                    programArgs.append("--special_removal")
                subprocess.run(programArgs)


def gatherResults():
    creatorSetup(-2.0, -2.0)
    allResults = []
    for subDir, dirs, files in os.walk(outputDirectory):
        for fileName in files:
            if not fileName.endswith(".pickle"):
                # It's not a pickle file, so skip it
                continue
            filePath = os.path.join(subDir, fileName)
            with open(filePath, "rb") as fileIn:
                results = pickle.load(fileIn)
                
            if results["version"] < 1.2:
                print("{} -- Unsupported version: {}".format(fileName, results["version"]))
                continue
            
            results["filePath"] = filePath

            if args.direct:
                toolbox = toolboxDirectSetup(results["benignEquation"], results["malwareEquation"],
                    1, 3, 17, results["testPoints"]["start"], results["testPoints"]["stop"],
                    results["testPoints"]["step"], results["insertion"]["start"], 
                    results["insertion"]["stop"]
                )
            else:
                toolbox = toolboxGaussianSetup(results["benignEquation"], results["malwareEquation"],
                    1, 3, 17, results["testPoints"]["start"], results["testPoints"]["stop"],
                    results["testPoints"]["step"], results["insertion"]["start"], 
                    results["insertion"]["stop"], -3, 3
                )

            results["toolbox"] = toolbox
            results["removal"]["generationsUsed"] = min(results["removal"]["maximumGenerationsAllowed"],
                      results["removal"]["generationsUsed"]
                    )
            results["creation"]["generationsUsed"] = min(results["creation"]["maximumGenerationsAllowed"],
                      results["creation"]["generationsUsed"]
                    )
            allResults.append(results)
    return allResults

def individualResultsAnalysis(allResults):
    for results in allResults:
        toolbox = results["toolbox"]
        if args.direct:
            plotTrojanCreation(toolbox.benignEquation, toolbox.malwareEquation,
                toolbox.pieceWiseFunction,
                toolbox.compile(results["creation"]["hallOfFame"][0]),
                toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                results["filePath"].replace("pickle", "directTrojanCreation.png")
            )
            plotTrojanRemoval(toolbox.benignEquation, toolbox.malwareEquation,
                toolbox.compile(results["creation"]["hallOfFame"][0]),
                toolbox.compile(results["removal"]["hallOfFame"][0]),
                toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                results["filePath"].replace("pickle", "directTrojanRemoval.png")
            )
        else:
            evolvedTrojan = toolbox.gaussianTrojan(results["creation"]["hallOfFame"][0], toolbox.benignEquation)
            plotTrojanCreation(toolbox.benignEquation, toolbox.malwareEquation,
                toolbox.pieceWiseFunction,
                evolvedTrojan,
                toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                results["filePath"].replace("pickle", "gaussianTrojanCreation.png")
            )
            evolvedBenign = toolbox.compile(results["removal"]["hallOfFame"][0])
            plotTrojanRemoval(toolbox.benignEquation, toolbox.malwareEquation,
                evolvedTrojan,
                evolvedBenign,
                toolbox.testPoints(), results["insertion"]["start"], results["insertion"]["stop"],
                results["filePath"].replace("pickle", "gaussianTrojanRemoval.png")
            )


def sortAllResultsIntoTypes(allResults, mode):
    def removeNumbers(string):
        return ''.join(c for c in string if not c.isdigit())

    types = {}
    for result in allResults:
      typeKey = "{}->{}".format(
              removeNumbers(result["malwareEquationType"]),
              removeNumbers(result["benignEquationType"])
      )

      if types.get(typeKey) is None:
          types[typeKey] = {"averageGensUsed": None, "results": list()}
      types[typeKey]["results"].append(result)

    for typeKey in types.keys():
      types[typeKey]["averageGensUsed"] = np.mean([r[mode]["generationsUsed"] for r in types[typeKey]["results"]])
    return types


def modeSpecificAnalysis(allResults, mode):
    print("Analysis: {}".format(mode.capitalize()))
    print("Average Fitness: {}".format(np.mean([results[mode]["hallOfFame"][0].fitness.values[0] for results in allResults])))
    print("Max Generations Used: {}".format(max(results[mode]["generationsUsed"]
        for results in allResults)
    ))
    print("Min Generations Used: {}".format(min(results[mode]["generationsUsed"]
        for results in allResults)
    ))
    print("Average Generations Used: {}".format(np.mean([results[mode]["generationsUsed"]
        for results in allResults])
    ))
    print("Average Ratio of Generations Used: {}".format(
        np.mean([results[mode]["generationsUsed"]/results[mode]["maximumGenerationsAllowed"]
            for results in allResults])
    ))

    sizeRatios = []
    for results in allResults:
        evolved = results[mode]["hallOfFame"][0]
        if type(evolved) == creator.DirectIndividual or type(evolved) == creator.RemovalIndividual:
            evolvedLength = len(evolved)
        elif type(evolved) == creator.GaussianIndividual:
            evolvedLength = len(evolved[3])
        else:
            raise ValueError("Unknown type: {}".format(type(evolved)))

        originalLength = len(results["toolbox"].manualEquation(results["benignEquation"]))
        sizeRatios.append(np.divide(evolvedLength, originalLength))

    print("Average {}/Benign: {}".format(mode.capitalize(), np.mean(sizeRatios)))
    
    if mode == "removal":
        equationAnalysis(allResults, mode)

  
def equationAnalysis(allResults, mode):
    # Save file of equation evolutions
    with open(os.path.join(outputDirectory, "{}-equationEvolutionText.txt".format(mode)), "w") as fileOut:
        seperatorLine = "--------------------\n"
        fileOut.write("Benign <-> Evolved {}\n{}".format(mode.capitalize(), seperatorLine))

        for results in allResults:
            # Gather the original and evovled
            original = results["toolbox"].manualEquation(results["benignEquation"]) # For consistency in spacing.
            evolved = results[mode]["hallOfFame"][0]
            def removeFloatingPoints(equationString):
                return equationString.replace("1.0","1").replace("0.0","0")
            origStr = removeFloatingPoints(str(original))
            if mode == "creation":
              evolStr = removeFloatingPoints(str(evolved[3]))
            else:
              evolStr = removeFloatingPoints(str(evolved))
            # Analyze the evolved
            originalInEvolved = origStr in evolStr
            exactDuplicate = origStr == evolStr
            # Determine if it's addition/subtraction by zero
            if originalInEvolved and not exactDuplicate:
                # Extract everything but the original equation
                extraction = evolStr.replace(origStr, "x")
                # Compile it
                extrFunc = results["toolbox"].compile(results["toolbox"].manualEquation(extraction))
                # Test if it always outputs the test point with the test points.
                sumTest = sum(testPoint - extrFunc(testPoint) for testPoint in results["toolbox"].testPoints())
                additionOfZero = sumTest == 0
            else:
                extraction = ""
                additionOfZero = False

            origRegex = origStr.replace("(","\(").replace(")","\)")
            for variable in ["-1", "1", "0", "x"]:
                origRegex = origRegex.replace(variable, "(.+?)")
            if extraction != "":
               evolToCheck = extraction
            else:
               evolToCheck = evolStr
            try:
              origGroups = re.search(origRegex, origStr).groups()
              evolGroups = re.search(origRegex, evolToCheck).groups()
              simpleVariableChanges = []
              for orig, evol in zip(origGroups, evolGroups):
                  if orig != evol:
                    simpleVariableChanges.append("{} -> {}".format(orig, evol))
              simpleVariableChanges = ", ".join(simpleVariableChanges)
            except AttributeError:
              simpleVariableChanges = "" 
            # Write out information
            fileOut.write("Equation Plotting Fitness: {}\n".format(evolved.fitness.values[0]))
            fileOut.write("Equation Size Fitness: {}\n".format(evolved.fitness.values[1] if len(evolved.fitness.values) > 1 else "N/A"))
            fileOut.write("Test Start and Stop: {} <-> {}\n".format(results["insertion"]["start"], results["insertion"]["stop"]))
            fileOut.write("Orig. in Evol.?: {}\n".format(originalInEvolved))
            fileOut.write("Exact Duplicate?: {}\n".format(exactDuplicate))
            fileOut.write("Addition of Zero?: {}\n".format(additionOfZero))
            # Simply write out the equations
            fileOut.write("Original: {}\n".format(origStr))
            fileOut.write("Evolved : {}\n".format(evolStr))
            fileOut.write("Simple Variable Changes: {}\n".format(simpleVariableChanges))
            # fileOut.write("Differences:\n")
            # for i,s in enumerate(difflib.ndiff(origStr, evolStr)):
                # if s[0] == ' ':
                    # continue
                # elif s[0] == '-':
                    # fileOut.write('Delete "{}" from position {}\n'.format(s[-1],i))
                # elif s[0] == '+':
                    # fileOut.write('Add "{}" to position {}\n'.format(s[-1],i))
            # End the section about this equation
            fileOut.write(seperatorLine)


def modeAndTypeSpecificAnalysis(types, mode):
    # Create a plot of the average generations used
    sortedByAverageGensUsed = sorted(list(types.keys()), key=lambda typeKey: types[typeKey]["averageGensUsed"])
    xs = np.arange(len(types))
    plt.bar(xs, [types[typeKey]["averageGensUsed"] for typeKey in sortedByAverageGensUsed], zorder=-1)
    for typeKey, x in zip(sortedByAverageGensUsed, xs):
        for result in types[typeKey]["results"]:
          if result[mode]["generationsUsed"] == result[mode]["maximumGenerationsAllowed"]:
            color="r"
          elif result[mode]["generationsUsed"] == 1:
            color="g"
          else:
            color="k"
          plt.scatter([x], result[mode]["generationsUsed"], color=color)

    plt.title("Generations Used -- {}".format(mode))
    plt.xlabel("Malware -> Benign")
    plt.xticks(xs,
            list(types.keys()),
            rotation='vertical'
    )
    plt.ylabel("Num. Gens. Used")
    plt.yticks(np.arange(0,2000,250))
    plt.grid()

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.2 # inch margin
    s = maxsize/plt.gcf().dpi*len(allResults)+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin, bottom=0.4)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    plt.savefig(os.path.join("presentationOutput", "{}_generations_used.png".format(mode)))
    plt.close()


def allResultsAnalysis(allResults):
    # All modes
    print("Analysis: Cross")

    sizeRatios = []
    for result in allResults:
        evolvedCreation = result["creation"]["hallOfFame"][0]
        if type(evolvedCreation) == creator.DirectIndividual or type(evolvedCreation) == creator.RemovalIndividual:
            evolvedCreationLength = len(evolvedCreation)
        elif type(evolvedCreation) == creator.GaussianIndividual:
            evolvedCreationLength = len(evolvedCreation[3])
        else:
            raise ValueError("Unknown type: {}".format(type(evolvedCreation)))

        evolvedRemoval = result["removal"]["hallOfFame"][0]
        if type(evolvedRemoval) == creator.DirectIndividual or type(evolvedRemoval) == creator.RemovalIndividual:
            evolvedRemovalLength = len(evolvedRemoval)
        elif type(evolvedRemoval) == creator.GaussianIndividual:
            evolvedRemovalLength = len(evolvedRemoval[3])
        else:
            raise ValueError("Unknown type: {}".format(type(evolvedRemoval)))

        sizeRatios.append(np.divide(evolvedRemovalLength, evolvedCreationLength))

    print("Average of Removal/Creation: {}".format(np.mean(sizeRatios)))


def produceLaTeXListOfEquations():
    filePath = os.path.join("presentationOutput", "equationsList.tex")

    with open(filePath, "w") as fileOut:
        fileOut.write("\\begin{itemize}\n")
        for equationName in sorted(equations.keys()):
            fileOut.write("\item \\textbf{{{}:}} {}\n".format(equationName, equations[equationName]))
        fileOut.write("\end{itemize}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip_evolution", action="store_true", default=False,
            help="Rather to run the evolution or not. Default is True"
        )
    parser.add_argument("--max_number_of_generations", type=int, default=2000,
            help="The maximum number of generations. Default is 2000"
    )
    parser.add_argument("--direct", action="store_true", default=False,
            help="Uses the direct manipluation of an equation instead of gausian"
    )
    parser.add_argument("--redo_removal", action="store_true", default=False,
            help="Redos only the removal part of the evolution process, if the pickle exists"
    )
    parser.add_argument("--skip_individual_analysis", action="store_true", default=False,
            help="Skips the analsyis/plotting of individual runs."
    )
    parser.add_argument("--skip_mode_specific_analysis", action="store_true", default=False,
            help="Skips the analsyis/plotting specific to creation/removal."
    )
    parser.add_argument("--skip_cross_analysis", action="store_true", default=False,
            help="Skips the analsyis/plotting relating to all runs in aggergate."
    )
    parser.add_argument("--skip_LaTeX_equation_list", action="store_true", default=False,
            help="Skips creating the LaTeX equation list."
    )
    parser.add_argument("--special_removal", action="store_true", default=False,
            help="Evolves based on the size of the benign equation as well as the outputs"
    )
    args = parser.parse_args()

    if not args.skip_evolution:
        runEvolution()

    # Gather the data
    allResults = gatherResults()
    
    # Analyze the data
    if not args.skip_individual_analysis:
      individualResultsAnalysis(allResults)

    if not args.skip_mode_specific_analysis:
      for mode in ["creation", "removal"]:
        modeSpecificAnalysis(allResults, mode)
        byTypes = sortAllResultsIntoTypes(allResults, mode)
        modeAndTypeSpecificAnalysis(byTypes, mode)

    if not args.skip_cross_analysis:
      allResultsAnalysis(allResults)

    if not args.skip_LaTeX_equation_list:
      produceLaTeXListOfEquations()

