from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import xml.etree.ElementTree as ET

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
        semantic_scholar_url: str,
        europe_pmc_url: str,
        arxiv_url: str,
        timeout: int = 8,
        crossref_mailto: str | None = None,
        semantic_scholar_api_key: str | None = None,
    ):
        self.openalex_url = openalex_url
        self.crossref_url = crossref_url
        self.semantic_scholar_url = semantic_scholar_url
        self.europe_pmc_url = europe_pmc_url
        self.arxiv_url = arxiv_url
        self.timeout = timeout
        self.crossref_mailto = crossref_mailto
        self.semantic_scholar_api_key = (
            semantic_scholar_api_key
        )

    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": (
                "Project-Axiom/0.2 "
                "(scientific-literature-research)"
            )
        }

    def search_openalex(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:

        response = requests.get(
            self.openalex_url,
            params={
                "search": query,
                "per-page": limit,
            },
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()
        papers = []

        for item in data.get("results", []):
            authors = []

            for author in item.get(
                "authorships",
                [],
            ):
                name = (
                    author
                    .get("author", {})
                    .get("display_name")
                )

                if name:
                    authors.append(name)

            primary_location = item.get(
                "primary_location",
                {},
            )

            papers.append(
                Paper(
                    title=item.get(
                        "title"
                    ) or "Untitled",
                    authors=authors,
                    year=item.get(
                        "publication_year"
                    ),
                    doi=item.get("doi"),
                    url=primary_location.get(
                        "landing_page_url"
                    ),
                    source="OpenAlex",
                    abstract=(
                        self._decode_openalex_abstract(
                            item.get(
                                "abstract_inverted_index"
                            )
                        )
                    ),
                )
            )

        return papers

    def search_crossref(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:

        params = {
            "query.bibliographic": query,
            "rows": limit,
        }

        if self.crossref_mailto:
            params["mailto"] = self.crossref_mailto

        response = requests.get(
            self.crossref_url,
            params=params,
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()
        papers = []

        items = (
            data
            .get("message", {})
            .get("items", [])
        )

        for item in items:
            authors = []

            for author in item.get(
                "author",
                [],
            ):
                given = author.get(
                    "given",
                    "",
                )
                family = author.get(
                    "family",
                    "",
                )

                name = f"{given} {family}".strip()

                if name:
                    authors.append(name)

            published = (
                item.get("published-print")
                or item.get("published-online")
                or item.get("published")
            )

            year = self._extract_year(
                published
            )

            title_values = item.get(
                "title",
                ["Untitled"],
            )

            title = (
                title_values[0]
                if title_values
                else "Untitled"
            )

            abstract = self._clean_html(
                item.get("abstract", "")
            )

            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    doi=item.get("DOI"),
                    url=item.get("URL"),
                    source="Crossref",
                    abstract=abstract,
                )
            )

        return papers

    def search_semantic_scholar(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:

        headers = self._headers()

        if self.semantic_scholar_api_key:
            headers["x-api-key"] = (
                self.semantic_scholar_api_key
            )

        response = requests.get(
            self.semantic_scholar_url,
            params={
                "query": query,
                "limit": limit,
                "fields": (
                    "title,authors,year,abstract,"
                    "url,externalIds,openAccessPdf"
                ),
            },
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()
        papers = []

        for item in data.get(
            "data",
            [],
        ):
            authors = [
                author.get("name")
                for author in item.get(
                    "authors",
                    [],
                )
                if author.get("name")
            ]

            external_ids = (
                item.get("externalIds")
                or {}
            )

            doi = external_ids.get("DOI")

            url = item.get("url")

            open_access = item.get(
                "openAccessPdf"
            )

            if open_access and open_access.get(
                "url"
            ):
                url = open_access["url"]

            papers.append(
                Paper(
                    title=item.get(
                        "title"
                    ) or "Untitled",
                    authors=authors,
                    year=item.get("year"),
                    doi=doi,
                    url=url,
                    source="Semantic Scholar",
                    abstract=(
                        item.get("abstract")
                        or ""
                    ),
                )
            )

        return papers

    def search_europe_pmc(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:

        response = requests.get(
            self.europe_pmc_url,
            params={
                "query": query,
                "format": "json",
                "pageSize": limit,
                "resultType": "core",
            },
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()
        papers = []

        for item in data.get(
            "resultList",
            {},
        ).get(
            "result",
            [],
        ):

            authors = []

            for author in item.get(
                "authorList",
                {},
            ).get(
                "author",
                [],
            ):
                full_name = (
                    author.get("fullName")
                    or author.get("authorName")
                )

                if full_name:
                    authors.append(full_name)

            doi = item.get("doi")

            url = None

            if item.get("pmcid"):
                url = (
                    "https://europepmc.org/articles/"
                    f"{item['pmcid']}"
                )
            elif item.get("pmid"):
                url = (
                    "https://europepmc.org/article/"
                    f"MED/{item['pmid']}"
                )

            papers.append(
                Paper(
                    title=item.get(
                        "title"
                    ) or "Untitled",
                    authors=authors,
                    year=self._safe_int(
                        item.get("pubYear")
                    ),
                    doi=doi,
                    url=url,
                    source="Europe PMC",
                    abstract=(
                        item.get("abstractText")
                        or ""
                    ),
                )
            )

        return papers

    def search_arxiv(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:

        response = requests.get(
            self.arxiv_url,
            params={
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": limit,
                "sortBy": "relevance",
                "sortOrder": "descending",
            },
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.text
        )

        namespace = {
            "atom": (
                "http://www.w3.org/2005/Atom"
            )
        }

        papers = []

        for entry in root.findall(
            "atom:entry",
            namespace,
        ):
            title = (
                entry.findtext(
                    "atom:title",
                    default="Untitled",
                    namespaces=namespace,
                )
                .strip()
            )

            abstract = (
                entry.findtext(
                    "atom:summary",
                    default="",
                    namespaces=namespace,
                )
                .strip()
            )

            published = entry.findtext(
                "atom:published",
                default="",
                namespaces=namespace,
            )

            year = None

            if published:
                year = self._safe_int(
                    published[:4]
                )

            authors = []

            for author in entry.findall(
                "atom:author",
                namespace,
            ):
                name = author.findtext(
                    "atom:name",
                    default="",
                    namespaces=namespace,
                )

                if name:
                    authors.append(
                        name.strip()
                    )

            url = None

            for link in entry.findall(
                "atom:link",
                namespace,
            ):
                href = link.attrib.get("href")

                if href:
                    url = href
                    break

            doi = None

            for identifier in entry.findall(
                "atom:id",
                namespace,
            ):
                identifier_text = (
                    identifier.text or ""
                )

                if "doi.org" in identifier_text:
                    doi = (
                        identifier_text
                        .split("doi.org/", 1)[-1]
                    )

            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=year,
                    doi=doi,
                    url=url,
                    source="arXiv",
                    abstract=abstract,
                )
            )

        return papers

    @staticmethod
    def _safe_int(
        value,
    ) -> int | None:

        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _extract_year(
        published,
    ) -> int | None:

        if not published:
            return None

        parts = published.get(
            "date-parts",
            [],
        )

        if not parts or not parts[0]:
            return None

        return LiteratureSearcher._safe_int(
            parts[0][0]
        )

    @staticmethod
    def _clean_html(
        text: str,
    ) -> str:

        if not text:
            return ""

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        return " ".join(
            text.split()
        )

    @staticmethod
    def _decode_openalex_abstract(
        inverted_index: dict[str, list[int]]
        | None,
    ) -> str:

        if not inverted_index:
            return ""

        words = []

        for word, positions in (
            inverted_index.items()
        ):
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


class SafeLiteratureSearcher(
    LiteratureSearcher
):

    def _safe_call(
        self,
        source: str,
        function,
        query: str,
        limit: int,
    ) -> LiteratureSearchResult:

        try:
            papers = function(
                query,
                limit,
            )

            return LiteratureSearchResult(
                papers=papers,
                source=source,
            )

        except (
            requests.RequestException,
            ET.ParseError,
            ValueError,
        ) as error:

            return LiteratureSearchResult(
                papers=[],
                source=source,
                error=str(error),
            )

    def search_with_status(
        self,
        query: str,
        limit: int = 10,
    ) -> list[LiteratureSearchResult]:

        jobs = {
            "OpenAlex": self.search_openalex,
            "Crossref": self.search_crossref,
            "Semantic Scholar": (
                self.search_semantic_scholar
            ),
            "Europe PMC": (
                self.search_europe_pmc
            ),
            "arXiv": self.search_arxiv,
        }

        results = []

        with ThreadPoolExecutor(
            max_workers=len(jobs)
        ) as executor:

            futures = {
                executor.submit(
                    self._safe_call,
                    source,
                    function,
                    query,
                    limit,
                ): source
                for source, function
                in jobs.items()
            }

            for future in as_completed(
                futures
            ):
                results.append(
                    future.result()
                )

        order = {
            "OpenAlex": 0,
            "Crossref": 1,
            "Semantic Scholar": 2,
            "Europe PMC": 3,
            "arXiv": 4,
        }

        results.sort(
            key=lambda item:
                order.get(
                    item.source,
                    99,
                )
        )

        return results

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:

        results = self.search_with_status(
            query=query,
            limit=limit,
        )

        papers = []

        for result in results:
            papers.extend(
                result.papers
            )

        return self._deduplicate(
            papers
        )

    @staticmethod
    def _normalise_title(
        title: str,
    ) -> str:

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
                paper.doi
                .lower()
                .strip()
                if paper.doi
                else None
            )

            title = cls._normalise_title(
                paper.title
            )

            if (
                doi
                and doi in seen_dois
            ):
                continue

            if (
                title
                and title in seen_titles
            ):
                continue

            if doi:
                seen_dois.add(doi)

            if title:
                seen_titles.add(title)

            unique.append(
                paper
            )

        return unique