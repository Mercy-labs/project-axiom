def generate_hypothesis(best_experiment, experiments):
    best_sunlight = best_experiment["sunlight"]
    best_growth = best_experiment["growth"]

    highest_sunlight = max(
        experiment["sunlight"] for experiment in experiments
    )

    lowest_sunlight = min(
        experiment["sunlight"] for experiment in experiments
    )

    if best_sunlight == highest_sunlight:
        hypothesis = (
            f"Greater sunlight may lead to greater plant growth. "
            f"The strongest result was {best_growth} growth at "
            f"{best_sunlight} hours of sunlight."
        )

    elif best_sunlight == lowest_sunlight:
        hypothesis = (
            f"Lower sunlight may be sufficient for plant growth. "
            f"The strongest result was {best_growth} growth at "
            f"{best_sunlight} hours of sunlight."
        )

    else:
        hypothesis = (
            f"Plant growth may be strongest around {best_sunlight} "
            f"hours of sunlight. The strongest result was "
            f"{best_growth} growth."
        )

    return hypothesis