from dataclasses import dataclass
import os


@dataclass
class Config:
    max_cycles: int = 6
    candidate_min: int = 1
    candidate_max: int = 20

    openalex_url: str = "https://api.openalex.org/works"
    crossref_url: str = "https://api.crossref.org/v1/works"
    semantic_scholar_url: str = (
        "https://api.semanticscholar.org/graph/v1/paper/search"
    )
    europe_pmc_url: str = (
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    )
    arxiv_url: str = (
        "https://export.arxiv.org/api/query"
    )

    request_timeout: int = 8
    api_url: str | None = None
    api_key: str | None = None
    crossref_mailto: str | None = None
    semantic_scholar_api_key: str | None = None

    @classmethod
    def from_environment(cls) -> "Config":
        return cls(
            max_cycles=int(
                os.getenv("AXIOM_MAX_CYCLES", "6")
            ),
            candidate_min=int(
                os.getenv("AXIOM_CANDIDATE_MIN", "1")
            ),
            candidate_max=int(
                os.getenv("AXIOM_CANDIDATE_MAX", "20")
            ),
            openalex_url=os.getenv(
                "AXIOM_OPENALEX_URL",
                "https://api.openalex.org/works",
            ),
            crossref_url=os.getenv(
                "AXIOM_CROSSREF_URL",
                "https://api.crossref.org/v1/works",
            ),
            semantic_scholar_url=os.getenv(
                "AXIOM_SEMANTIC_SCHOLAR_URL",
                "https://api.semanticscholar.org/graph/v1/paper/search",
            ),
            europe_pmc_url=os.getenv(
                "AXIOM_EUROPE_PMC_URL",
                "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            ),
            arxiv_url=os.getenv(
                "AXIOM_ARXIV_URL",
                "https://export.arxiv.org/api/query",
            ),
            request_timeout=int(
                os.getenv("AXIOM_REQUEST_TIMEOUT", "8")
            ),
            api_url=os.getenv("AXIOM_API_URL"),
            api_key=os.getenv("AXIOM_API_KEY"),
            crossref_mailto=os.getenv(
                "AXIOM_CROSSREF_MAILTO"
            ),
            semantic_scholar_api_key=os.getenv(
                "AXIOM_SEMANTIC_SCHOLAR_API_KEY"
            ),
        )