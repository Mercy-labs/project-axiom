def analyse_experiment(growth):
    average = sum(growth) / len(growth)
    highest = max(growth)
    lowest = min(growth)

    return average, highest, lowest


if __name__ == "__main__":
    growth = [10, 25, 32, 18, 40]

    average, highest, lowest = analyse_experiment(growth)

    print("Growth results:", growth)
    print("Average:", average)
    print("Highest:", highest)
    print("Lowest:", lowest)