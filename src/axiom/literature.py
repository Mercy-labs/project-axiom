from dataclasses import dataclass
import re

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


class LiteratureSearchResult:
    def __init__(
        self,
        papers: list[Paper],
        source: str,
        error: str | None = None,
    ):
        self.papers = papers
        self.source = source
        self.error = error


class LiteratureSearcher:
    def __init__(
        self,
        openalex_url: str,
        crossref_url: str,
        timeout: int = 10,
    ):
        self.openalex_url = openalex_url
        self.crossref_url = crossref_url
        self.timeout = timeout

    def search_openalex(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Paper]:

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

            primary_location = item.get(
                "primary_location",
                {},
            )

            papers.append(
                Paper(
                    title=item.get("title") or "Untitled",
                    authors=authors,
                    year=item.get("publication_year"),
                    doi=item.get("doi"),
                    url=primary_location.get(
                        "landing_page_url"
                    ),
                    source="OpenAlex",
                    abstract=self._decode_openalex_abstract(
                        item.get("abstract_inverted_index")
                    ),
                )
            )

        return papers

    def search_crossref(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Paper]:

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

        for item in data.get(
            "message",
            {},
        ).get(
            "items",
            [],
        ):

            authors = []

            for author in item.get(
                "author",
                [],
            ):
                given = author.get("given", "")
                family = author.get("family", "")

                name = f"{given} {family}".strip()

                if name:
                    authors.append(name)

            published = (
                item.get("published-print")
                or item.get("published")
            )

            year = None

            if published:
                parts = published.get(
                    "date-parts",
                    [],
                )

                if parts and parts[0]:
                    year = parts[0][0]

            titles = item.get(
                "title",
                ["Untitled"],
            )

            title = titles[0] if titles else "Untitled"

            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    doi=item.get("DOI"),
                    url=item.get("URL"),
                    source="Crossref",
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
                words.append(
                    (position, word)
                )

        words.sort(
            key=lambda item: item[0]
        )

        return " ".join(
            word
            for _, word in words
        )


class SafeLiteratureSearcher(LiteratureSearcher):

    def search_with_status(
        self,
        query: str,
        limit: int = 5,
    ) -> list[LiteratureSearchResult]:

        results = []

        try:
            papers = self.search_openalex(
                query,
                limit,
            )

            results.append(
                LiteratureSearchResult(
                    papers=papers,
                    source="OpenAlex",
                )
            )

        except requests.RequestException as error:
            results.append(
                LiteratureSearchResult(
                    papers=[],
                    source="OpenAlex",
                    error=str(error),
                )
            )

        try:
            papers = self.search_crossref(
                query,
                limit,
            )

            results.append(
                LiteratureSearchResult(
                    papers=papers,
                    source="Crossref",
                )
            )

        except requests.RequestException as error:
            results.append(
                LiteratureSearchResult(
                    papers=[],
                    source="Crossref",
                    error=str(error),
                )
            )

        return results

    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> list[Paper]:

        results = self.search_with_status(
            query=query,
            limit=limit,
        )

        papers = []

        for result in results:
            papers.extend(result.papers)

        return self._deduplicate(
            papers
        )

    @staticmethod
    def _normalise_title(title: str) -> str:
        return re.sub(
            r"[^a-z0-9]+",
            " ",
            title.lower(),
        ).strip()

    @classmethod
    def _deduplicate(
        cls,
        papers: list[Paper],
    ) -> list[Paper]:

        seen_dois = set()
        seen_titles = set()
        unique = []

        for paper in papers:

            doi = (
                paper.doi.lower().strip()
                if paper.doi
                else None
            )

            title = cls._normalise_title(
                paper.title
            )

            if doi and doi in seen_dois:
                continue

            if title and title in seen_titles:
                continue

            if doi:
                seen_dois.add(doi)

            if title:
                seen_titles.add(title)

            unique.append(paper)

        return unique