#!/bin/bash

./main.py "$(cat complexEquations/complex_equation1.txt)" "$(cat complexEquations/complex_equation2.txt)" True --number_of_generations 2000; ./main.py "$(cat output/TrojanCreation--halloffame-0--equation_written.txt)" "$(cat complexEquations/complex_equation1.txt)" False
