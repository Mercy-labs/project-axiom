from dataclasses import dataclass
from typing import Any
import requests


@dataclass
class Paper:
    title: str
    authors: list[str]
    year: int | None
    doi: str | None
    url: str | None
    source: str
    abstract: str = ""


class LiteratureSearcher:
    def __init__(self, openalex_url: str, crossref_url: str, timeout: int = 10):
        self.openalex_url = openalex_url
        self.crossref_url = crossref_url
        self.timeout = timeout

    def search_openalex(self, query: str, limit: int = 5) -> list[Paper]:
        params = {
            "search": query,
            "per-page": limit,
        }

        response = requests.get(
            self.openalex_url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        papers = []

        for item in data.get("results", []):
            authors = []

            for author in item.get("authorships", []):
                name = author.get("author", {}).get("display_name")
                if name:
                    authors.append(name)

            papers.append(
                Paper(
                    title=item.get("title") or "Untitled",
                    authors=authors,
                    year=item.get("publication_year"),
                    doi=item.get("doi"),
                    url=item.get("primary_location", {}).get("landing_page_url"),
                    source="OpenAlex",
                    abstract=self._decode_openalex_abstract(
                        item.get("abstract_inverted_index")
                    ),
                )
            )

        return papers

    def search_crossref(self, query: str, limit: int = 5) -> list[Paper]:
        params = {
            "query": query,
            "rows": limit,
        }

        response = requests.get(
            self.crossref_url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        papers = []

        for item in data.get("message", {}).get("items", []):
            authors = [
                author.get("given", "") + " " + author.get("family", "")
                for author in item.get("author", [])
            ]

            authors = [author.strip() for author in authors if author.strip()]

            published = item.get("published-print") or item.get("published")
            year = None

            if published:
                parts = published.get("date-parts", [])
                if parts and parts[0]:
                    year = parts[0][0]

            papers.append(
                Paper(
                    title=item.get("title", ["Untitled"])[0],
                    authors=authors,
                    year=year,
                    doi=item.get("DOI"),
                    url=item.get("URL"),
                    source="Crossref",
                    abstract="",
                )
            )

        return papers

    @staticmethod
    def _decode_openalex_abstract(
        inverted_index: dict[str, list[int]] | None,
    ) -> str:
        if not inverted_index:
            return ""

        words = []

        for word, positions in inverted_index.items():
            for position in positions:
                words.append((position, word))

        words.sort(key=lambda item: item[0])

        return " ".join(word for _, word in words)


class SafeLiteratureSearcher(LiteratureSearcher):
    """
    Wrapper that allows Axiom to continue operating if an external
    literature service is unavailable.
    """

    def search(self, query: str, limit: int = 5) -> list[Paper]:
        papers = []

        try:
            papers.extend(self.search_openalex(query, limit))
        except requests.RequestException:
            pass

        try:
            papers.extend(self.search_crossref(query, limit))
        except requests.RequestException:
            pass

        return papers