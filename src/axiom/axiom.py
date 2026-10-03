from .analysis import analyse_growth, find_best_experiment
from .hypotheses import generate_hypothesis
from .experiments import create_next_experiment
from .data import EXPERIMENTS
from .memory import remember, show_memory


def main():
    print("Axiom v0.3 starting...")

    experiments = EXPERIMENTS

    growth_results = []

    for experiment in experiments:
        growth_results.append(experiment["growth"])

    analysis = analyse_growth(growth_results)
    best = find_best_experiment(experiments)

    hypothesis = generate_hypothesis(best)
    next_experiment = create_next_experiment(best)

    research_entry = {
        "experiment": best["name"],
        "result": best["growth"],
        "hypothesis": hypothesis
    }

    remember(research_entry)

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

    print()
    show_memory()


if __name__ == "__main__":
    main()