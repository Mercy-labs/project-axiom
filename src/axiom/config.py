from dataclasses import dataclass
import os


@dataclass
class Config:
    max_cycles: int = 6
    candidate_min: int = 1
    candidate_max: int = 20
    openalex_url: str = "https://api.openalex.org/works"
    crossref_url: str = "https://api.crossref.org/works"
    api_url: str | None = None
    api_key: str | None = None

    @classmethod
    def from_environment(cls) -> "Config":
        return cls(
            max_cycles=int(os.getenv("AXIOM_MAX_CYCLES", "6")),
            candidate_min=int(os.getenv("AXIOM_CANDIDATE_MIN", "1")),
            candidate_max=int(os.getenv("AXIOM_CANDIDATE_MAX", "20")),
            openalex_url=os.getenv(
                "AXIOM_OPENALEX_URL",
                "https://api.openalex.org/works",
            ),
            crossref_url=os.getenv(
                "AXIOM_CROSSREF_URL",
                "https://api.crossref.org/works",
            ),
            api_url=os.getenv("AXIOM_API_URL"),
            api_key=os.getenv("AXIOM_API_KEY"),
        )