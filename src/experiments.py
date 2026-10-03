def create_next_experiment(best_experiment):
    return {
        "name": "Next Experiment",
        "plant": best_experiment["plant"],
        "sunlight": best_experiment["sunlight"] + 2
    }