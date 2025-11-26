import random
import math
from app.Logic.Evaluator import evaluate
from ConfigManager import ConfigManager
from app.Logic.TemperatureCooling import cool

def generateNeighbor(allocation: dict):
    neighbor = allocation.copy()
    resources = list(neighbor.keys())
    A, B = random.sample(resources,2)
    neighbor[A], neighbor[B] =  neighbor[B], neighbor[A] 
    return neighbor 

def simulatedAnnealing(initialAllocation: dict, progressCallback = None):

    print(str(evaluate(initialAllocation)))
    config = ConfigManager().getConfig()   
    maxI = config["max_iterations"]
    solution = initialAllocation
    current = solution
    temperature= config.get("initial_temperature", 1)
    i= 0

    currentCost, currentCostsByConstraint  = evaluate(initialAllocation)
    solutionCost = currentCost
    solutionCostsByConstraint = currentCostsByConstraint

    iterationsWithoutImprove = 0
    iterationsWithoutChanges = 0
    maxWithoutImprove = 0
    maxWithoutChanges = 0

    if progressCallback:
        samples = config["samples_for_statistics"]
        checkpoint = max(1, maxI // samples)

    while i < maxI and solutionCost > 0:
        i+=1
        candidate = generateNeighbor(current)
        candidateEvaluation = evaluate(candidate)
        difference = candidateEvaluation[0] - currentCost
        if difference < 0:
            current = candidate
            currentCost= candidateEvaluation[0]
            currentCostsByConstraint=candidateEvaluation[1]
            iterationsWithoutImprove = 0
            iterationsWithoutChanges = 0

            if currentCost < solutionCost:
                solution = candidate
                solutionCost = currentCost
                solutionCostsByConstraint = currentCostsByConstraint

        elif math.exp(-difference/temperature) > random.random():
            current = candidate
            currentCost=candidateEvaluation[0]
            currentCostsByConstraint=candidateEvaluation[1]
            iterationsWithoutChanges = 0
        else:
            iterationsWithoutChanges += 1
            iterationsWithoutImprove += 1

        maxWithoutImprove = max(maxWithoutImprove, iterationsWithoutImprove)
        maxWithoutChanges = max(maxWithoutChanges, iterationsWithoutChanges)
        temperature = cool(temperature, i)

        if progressCallback and i % checkpoint == 0:
            stats = {
                "progressPercent": int((i / maxI) * 100),
                "iteration": i,
                "bestCost": solutionCost,
                "currentCost": currentCost,
                "temperature": temperature,
                "iterationsWithoutImprove": iterationsWithoutImprove,
                "iterationsWithoutChanges": iterationsWithoutChanges,
                "maxWithoutImproveInterval": maxWithoutImprove,
                "maxWithoutChangesInterval": maxWithoutChanges,
                "currentCostsByConstraint": currentCostsByConstraint,
                "bestCostsByConstraint": solutionCostsByConstraint
            }
            progressCallback(stats, solution)

            # reset de máximos del intervalo
            maxWithoutImprove = iterationsWithoutImprove
            maxWithoutChanges = iterationsWithoutChanges

    print("fin del algoritmo")
    return solution
