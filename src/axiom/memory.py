research_memory = []


def remember(entry):
    research_memory.append(entry)


def get_memory():
    return research_memory


def show_memory():
    print("Axiom Research Memory")

    if not research_memory:
        print("No research recorded yet.")
        return

    for entry in research_memory:
        print()
        print("Experiment:", entry["experiment"])
        print("Result:", entry["result"])
        print("Hypothesis:", entry["hypothesis"])