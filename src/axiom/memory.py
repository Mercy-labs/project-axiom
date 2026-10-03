import json
from pathlib import Path


MEMORY_FILE = Path(__file__).parent / "memory.json"


def load_memory():
    if not MEMORY_FILE.exists():
        return []

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def remember(entry):
    memory = load_memory()
    memory.append(entry)

    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def get_memory():
    return load_memory()


def show_memory():
    memory = load_memory()

    print("Axiom Research Memory")

    if not memory:
        print("No research recorded yet.")
        return

    for entry in memory:
        print()
        print("Experiment:", entry["experiment"])
        print("Result:", entry["result"])
        print("Hypothesis:", entry["hypothesis"])