import copy
import csv
import glob
import math
import sys
import os
import random
import matplotlib.pyplot as plt

DATA_PATH = './data'


def parseData(file):
    csvFile = open(file)
    reader = csv.reader(csvFile, quoting=csv.QUOTE_NONNUMERIC)
    set = []
    for line in reader:
        for item in line:
            set.append(item)
    return set


def optimalStop(generator, samples, tests):
    print(f"Finding Optimal Stopping Point for Distribution of Size {samples}")

    accuracies = testStop(generator, samples, tests)
    stoppingPoints = [i for i in range(samples)]
    plt.title("Accuracy of Various Stopping Points for the Stopping Algorithm")
    plt.xlabel("Stopping Point")
    plt.ylabel("Accuracy of Stopping Algorithm")
    plt.plot(stoppingPoints, accuracies, 'r')
    plt.show()
    stoppingPoint = -1
    bestAccuracy = -1
    for i in range(len(accuracies)):
        if accuracies[i] > bestAccuracy:
            bestAccuracy = accuracies[i]
            stoppingPoint = i

    print(f"    Optimal Stopping Point (Human Indexed): {stoppingPoint + 1}")
    print(f"    Optimal Stopping Point as a Percentage: {(stoppingPoint + 1) / samples}")
    print(f"    Accuracy of Optimal Stopping POint: {bestAccuracy}")


def optimalStopWithCost(generator, samples, tests, cost):
    print(f"Finding Optimal Stopping Point for Distribution of Size {samples} and Exploration Cost of {cost}")

    accuracies = testStopWithCost(generator, samples, tests, cost)
    stoppingPoints = [i for i in range(samples)]
    plt.title("Accuracy of Various Stopping Points in the Algorithm (With Cost)")
    plt.xlabel("Stopping Point")
    plt.ylabel("Accuracy of Stopping Algorithm")
    plt.plot(stoppingPoints, accuracies, 'r')
    plt.show()
    stoppingPoint = -1
    bestAccuracy = -1
    for i in range(len(accuracies)):
        if accuracies[i] > bestAccuracy:
            bestAccuracy = accuracies[i]
            stoppingPoint = i

    print(f"    Optimal Stopping Point (Human Indexed): {stoppingPoint + 1}")
    print(f"    Optimal Stopping Point as a Percentage: {(stoppingPoint + 1) / samples}")
    print(f"    Accuracy of Optimal Stopping POint: {bestAccuracy}")


def testStop(generator, samples, tests):
    accuracies = [0 for i in range(samples)]
    for i in range(tests):
        randList = generator(samples)
        trueMax = max(randList)
        for j in range(1, samples):
            tempMax = max(randList[:j + 1])
            for k in range(j + 1, samples):
                if randList[k] > tempMax:
                    if randList[k] == trueMax:
                        accuracies[j] += 1
                    break

    return [accuracies[i] / tests for i in range(samples)]


def testStopWithCost(generator, samples, tests, cost):
    accuracies = [0 for i in range(samples)]
    for i in range(tests):
        randListBase = generator(samples)
        randList = [randListBase[i] - (i + 1) * cost for i in range(len(randListBase))]
        trueMax = max(randList)
        for j in range(1, samples):
            tempMax = max(randList[:j + 1])
            for k in range(j + 1, samples):
                if randList[k] > tempMax:
                    if randList[k] == trueMax:
                        accuracies[j] += 1
                    break

    return [accuracies[i] / tests for i in range(samples)]


def generateUniform(minimum, maximum, num):
    return [random.uniform(minimum, maximum) for i in range(num)]


def generateNormal(mean, deviation, num, lowerBound=-math.inf, upperBound=math.inf):
    randList = [random.normalvariate(mean, deviation) for i in range(num)]

    for i in range(len(randList)):
        if randList[i] < lowerBound:
            randList[i] = lowerBound
        elif randList[i] > upperBound:
            randList[i] = upperBound

    return randList


def createFileGen(file):
    data = parseData(file)

    def fileGen(num):
        random.shuffle(data)
        return data[:num]

    return fileGen


def optimalSearch(dataSet):
    stoppingPoint = math.ceil(1 / math.e * len(dataSet)) - 1
    tempMax = max(dataSet[:stoppingPoint + 1])
    for i in range(stoppingPoint + 1, len(dataSet)):
        if dataSet[i] > tempMax:
            return dataSet[i]

    return dataSet[-1]


def comprimisingSearch(dataSet, maxThreshHold):
    stoppingPoint = math.ceil(1 / math.e * len(dataSet)) - 1
    threshHoldPer = maxThreshHold / (len(dataSet) - stoppingPoint - 1)
    tempMax = max(dataSet[:stoppingPoint + 1])
    currentThreshold = threshHoldPer
    for i in range(stoppingPoint + 1, len(dataSet)):
        if math.fabs(dataSet[i] - tempMax) / tempMax < currentThreshold:
            return dataSet[i]
        currentThreshold += threshHoldPer

    return dataSet[-1]


def uniformTest():
    uniform = lambda x: generateUniform(0, 1000, x)
    optimalStop(uniform, 100, 1000)


def normalTest():
    normal = lambda x: generateNormal(50, 10, x, 0, 100)
    optimalStop(normal, 100, 1000)


def filesTest():
    files = glob.glob(f"{DATA_PATH}/*.csv")

    if len(files) == 0:
        print("    ERROR: No Data Files Given")
        return

    for file in files:
        title = os.path.basename(file)
        data = parseData(file)
        print(f"    Running Optimal Algorithm on {title}")
        if len(data) == 0:
            print("        ERROR: File Lacks Data or is Incorrectly formatted")
        trueMax = max(data)
        guess = optimalSearch(data)
        print(f"        True Max: {trueMax}")
        print(f"        Guess: {guess}")


def accuracyTest(dataSet, algorithm, iterations):
    trueMax = max(dataSet)
    copyData = copy.deepcopy(dataSet)
    correct = 0
    for i in range(iterations):
        random.shuffle(copyData)
        guess = algorithm(copyData)
        if guess == trueMax:
            correct += 1
    return correct / iterations


def filesTest2():
    files = glob.glob(f"{DATA_PATH}/*.csv")

    if len(files) == 0:
        print("    ERROR: No Data Files Given")
        return

    for file in files:
        title = os.path.basename(file)
        data = parseData(file)
        print(f"    Running Compromising Algorithm on {title}")
        if len(data) == 0:
            print("        ERROR: File Lacks Data or is Incorrectly formatted")
        trueMax = max(data)
        guess = comprimisingSearch(data, 0.5)
        print(f"        True Max: {trueMax}")
        print(f"        Guess: {guess}")


def unknownTest(file):
    print("TESTING ALGORITHMS ON STATIC DATA SETS")
    title = os.path.basename(file)
    data = parseData(file)
    print(f"    Running Optimal Algorithm on {title}")
    if len(data) == 0:
        print("        ERROR: File Lacks Data or is Incorrectly formatted")
    trueMax = max(data)
    guess = optimalSearch(data)
    accuracy = accuracyTest(data, optimalSearch, 1000)
    print(f"        True Max: {trueMax}")
    print(f"        Guess: {guess}")
    print(f"        Accuracy Over 1000 Random Draws: {accuracy}")
    print(f"    Running Compromising Algorithm on {title}")
    trueMax = max(data)
    guess = comprimisingSearch(data, 0.5)
    accuracy = accuracyTest(data, lambda x: comprimisingSearch(x, 0.5), 1000)
    print(f"        True Max: {trueMax}")
    print(f"        Guess: {guess}")
    print(f"        Accuracy Over 1000 Random Draws: {accuracy}")
    print(f"    Running Data Set 1 Algorithm (3.7% Stop Point) on {title}")
    trueMax = max(data)
    guess = optimalSearchGeneric(data, 0.037)
    accuracy = accuracyTest(data, lambda x: optimalSearchGeneric(x, 0.037), 1000)
    print(f"        True Max: {trueMax}")
    print(f"        Guess: {guess}")
    print(f"        Accuracy Over 1000 Random Draws: {accuracy}")
    print(f"    Running Data Set 2 Algorithm (30% Stop Point) on {title}")
    trueMax = max(data)
    guess = optimalSearchGeneric(data, 0.30)
    accuracy = accuracyTest(data, lambda x: optimalSearchGeneric(x, 0.30), 1000)
    print(f"        True Max: {trueMax}")
    print(f"        Guess: {guess}")
    print(f"        Accuracy Over 1000 Random Draws: {accuracy}")



def uniformCostTest():
    uniform = lambda x: generateUniform(0, 1000, x)
    optimalStopWithCost(uniform, 100, 1000, 1)


def normalCostTest():
    normal = lambda x: generateNormal(50, 10, x, 0, 100)
    optimalStopWithCost(normal, 100, 1000, 1)

def optimalFileTest1():
    generator = createFileGen('./data/scenario1.csv')
    optimalStop(generator, 1000, 1000)
def optimalFileTest2():
    generator = createFileGen('./data/scenario2.csv')
    optimalStop(generator, 1000, 1000)

def optimalSearchGeneric(dataSet, stoppingPercentage):
    stoppingPoint = math.ceil(stoppingPercentage * len(dataSet)) - 1
    tempMax = max(dataSet[:stoppingPoint + 1])
    for i in range(stoppingPoint + 1, len(dataSet)):
        if dataSet[i] > tempMax:
            return dataSet[i]

    return dataSet[-1]


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("RUNNING UNIFORM TEST")
        print("--------------------")
        uniformTest()
        print("\n\n\n")
        print("RUNNING NORMAL TEST")
        print("-------------------")
        normalTest()
        print("\n\n\n")
        print("RUNNING OPTIMAL ALGORITHM ON TEST FILES")
        print("---------------------------------------")
        filesTest()
        print("\n\n\n")
        print("RUNNING COMPROMISING ALGORITHM ON TEST FILES")
        print("---------------------------------------")
        filesTest2()
        print("\n\n\n")
        print("RUNNING UNIFORM TEST WITH COST")
        print("------------------------------")
        uniformCostTest()
        print("\n\n\n")
        print("RUNNING NORMAL TEST WITH COST")
        print("-----------------------------")
        normalCostTest()
        print("\n\n\n")
        print("RUNNING OPTIMAL FILE TEST 1")
        print("---------------------------")
        optimalFileTest1()
        print("\n\n\n")
        print("RUNNING OPTIMAL FILE TEST 2")
        print("---------------------------")
        optimalFileTest2()
        print("\n\n\n")
        sys.exit(0)
    elif len(sys.argv) == 2:
        if sys.argv[1] != "-help":
            unknownTest(sys.argv[1])
            sys.exit(0)

    print("ERROR: Unknown Usage")
    print("USAGE:")
    print("    python HW1_Fitzgerald_Jacob.py -> Runs Tests")
    print("    python HW1_Fitzgerald_Jacob.py [File] -> Runs Search Algorithms on a File Based Data Set")
    print("    python HW1_Fitzgerald_Jacob.py -help -> This Message")
