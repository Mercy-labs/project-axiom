import json
from pathlib import Path


MEMORY_FILE = (
    Path(__file__).parent
    / "research_memory.json"
)


class ResearchMemory:

    def __init__(self):
        self.entries = self._load()

    def _load(self):

        if not MEMORY_FILE.exists():
            return []

        try:
            with open(
                MEMORY_FILE,
                "r",
            ) as file:
                return json.load(file)

        except (
            json.JSONDecodeError,
            OSError,
        ):
            return []

    def save(self):

        with open(
            MEMORY_FILE,
            "w",
        ) as file:

            json.dump(
                self.entries,
                file,
                indent=4,
            )

    def remember(
        self,
        entry,
    ):

        self.entries.append(entry)
        self.save()

    def all(self):
        return self.entries

    def latest(self):

        if not self.entries:
            return None

        return self.entries[-1]

    def best_supported_hypothesis(self):

        supported = [
            entry
            for entry in self.entries
            if entry.get("status")
            == "supported"
        ]

        if not supported:
            return None

        return max(
            supported,
            key=lambda entry:
            entry.get(
                "confidence",
                0,
            ),
        )