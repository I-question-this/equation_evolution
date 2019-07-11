import numpy as np
import operator
import random
from deap import gp

# Create the primatives
# Protected operators
def protectedDiv(left, right):
    if right == 0:
        return 0
    else:
        return left / right

def protectedPow(base, exponent):
    if base == 0:
        return 0

    result = np.power(base, exponent, dtype=np.float_)
    return 0 if np.isinf(result) or np.isnan(result) else result

# Create the primative set
pset = gp.PrimitiveSet("MainPset", arity=1)
pset.renameArguments(ARG0='x')

pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protectedDiv, 2, name="div")
pset.addPrimitive(protectedPow, 2, name="pow")
pset.addPrimitive(operator.neg, 1)
pset.addPrimitive(np.cos, 1)
pset.addPrimitive(np.sin, 1)
pset.addEphemeralConstant("rand101",
    lambda: np.float_(random.randint(-1,1))
)
