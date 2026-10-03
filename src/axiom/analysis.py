def analyse_growth(growth):
    average = sum(growth) / len(growth)
    highest = max(growth)
    lowest = min(growth)

    return {
        "average": average,
        "highest": highest,
        "lowest": lowest
    }


def find_best_experiment(experiments):
    best_experiment = None
    best_growth = 0

    for experiment in experiments:
        if experiment["growth"] > best_growth:
            best_growth = experiment["growth"]
            best_experiment = experiment

    return best_experiment