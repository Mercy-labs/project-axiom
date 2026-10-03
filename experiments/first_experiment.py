def analyse_experiment(growth):
    average = sum(growth) / len(growth)
    highest = max(growth)
    lowest = min(growth)

    analysis = {
        "average": average,
        "highest": highest,
        "lowest": lowest
    }

    return analysis


def find_best_experiment(experiments):
    best_experiment = None
    best_growth = 0

    for experiment in experiments:
        if experiment["growth"] > best_growth:
            best_growth = experiment["growth"]
            best_experiment = experiment

    return best_experiment


def generate_hypothesis(best_experiment):
    hypothesis = (
        "Higher sunlight may lead to greater plant growth."
    )

    return hypothesis


def propose_next_experiment(best_experiment):
    next_experiment = {
        "name": "Next Experiment",
        "plant": best_experiment["plant"],
        "sunlight": best_experiment["sunlight"] + 2
    }

    return next_experiment


if __name__ == "__main__":
    experiment_a = {
        "name": "Experiment A",
        "plant": "maize",
        "sunlight": 6,
        "growth": 25
    }

    experiment_b = {
        "name": "Experiment B",
        "plant": "maize",
        "sunlight": 10,
        "growth": 40
    }

    experiment_c = {
        "name": "Experiment C",
        "plant": "maize",
        "sunlight": 8,
        "growth": 32
    }

    experiments = [
        experiment_a,
        experiment_b,
        experiment_c
    ]

    growth_results = [25, 40, 32]

    analysis = analyse_experiment(growth_results)
    best = find_best_experiment(experiments)

    hypothesis = generate_hypothesis(best)
    next_experiment = propose_next_experiment(best)

    print("Experiment analysis:")
    print("Average growth:", analysis["average"])
    print("Highest growth:", analysis["highest"])
    print("Lowest growth:", analysis["lowest"])

    print()
    print("Best experiment:", best["name"])
    print("Best growth:", best["growth"])

    print()
    print("Hypothesis:", hypothesis)

    print()
    print("Proposed next experiment:")
    print("Plant:", next_experiment["plant"])
    print("Sunlight:", next_experiment["sunlight"])