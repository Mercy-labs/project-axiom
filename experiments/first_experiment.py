def experiment():
    growth = [10, 25, 32, 18, 40]

    average = sum(growth) / len(growth)
    highest = max(growth)
    lowest = min(growth)

    print("Growth results:", growth)
    print("Average:", average)
    print("Highest:", highest)
    print("Lowest:", lowest)


if __name__ == "__main__":
    experiment()