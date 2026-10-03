def generate_hypothesis(best_experiment):
    sunlight = best_experiment["sunlight"]

    return (
        f"Higher sunlight may lead to greater plant growth. "
        f"The strongest result so far occurred at {sunlight} hours of sunlight."
    )