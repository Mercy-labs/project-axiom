from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class MemoryEntry:
    cycle: int
    hypothesis: str
    experiment: str
    observation: float
    conclusion: str
    confidence: float


class ResearchMemory:
    def __init__(self, path: str = "outputs/research_memory.json"):
        self.path = Path(path)
        self.entries: list[MemoryEntry] = []

    def remember(self, entry: MemoryEntry) -> None:
        self.entries.append(entry)

    def save(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            json.dumps(
                [asdict(entry) for entry in self.entries],
                indent=2,
            ),
            encoding="utf-8",
        )