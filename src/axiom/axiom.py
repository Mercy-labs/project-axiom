from analysis import analyse_growth, find_best_experiment
from hypotheses import generate_hypothesis
from experiments import create_next_experiment


def main():
    print("Axiom v0.2 starting...")

    experiments = [
        {
            "name": "Experiment A",
            "plant": "maize",
            "sunlight": 6,
            "growth": 25
        },
        {
            "name": "Experiment B",
            "plant": "maize",
            "sunlight": 10,
            "growth": 40
        },
        {
            "name": "Experiment C",
            "plant": "maize",
            "sunlight": 8,
            "growth": 32
        }
    ]

    growth_results = [25, 40, 32]

    analysis = analyse_growth(growth_results)
    best = find_best_experiment(experiments)

    hypothesis = generate_hypothesis(best)
    next_experiment = create_next_experiment(best)

    print("Experiment analysis:")
    print("Average growth:", analysis["average"])
    print("Highest growth:", analysis["highest"])
    print("Lowest growth:", analysis["lowest"])

    print()
    print("Best experiment:", best["name"])
    print("Growth:", best["growth"])

    print()
    print("Hypothesis:", hypothesis)

    print()
    print("Next experiment:")
    print("Plant:", next_experiment["plant"])
    print("Sunlight:", next_experiment["sunlight"])


if __name__ == "__main__":
    main()