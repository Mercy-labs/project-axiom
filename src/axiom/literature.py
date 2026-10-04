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
    relevance: float = 0.0


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
    STOP_WORDS = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "for",
        "with",
        "is",
        "are",
        "was",
        "were",
        "that",
        "this",
        "as",
        "by",
        "from",
        "how",
        "does",
        "do",
        "what",
        "which",
        "why",
        "when",
        "where",
        "into",
        "their",
        "they",
        "them",
        "than",
        "can",
        "may",
        "be",
        "a",
        "an",
    }

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
                "Project-Axiom/0.3 "
                "(scientific-literature-research)"
            )
        }

    # ---------------------------------------------------------
    # Query planning
    # ---------------------------------------------------------

    @classmethod
    def _tokens(cls, text: str) -> set[str]:
        words = re.findall(
            r"[a-zA-Z0-9][a-zA-Z0-9\-]+",
            text.lower(),
        )

        return {
            word
            for word in words
            if word not in cls.STOP_WORDS
            and len(word) > 2
        }

    @classmethod
    def _build_queries(
        cls,
        question: str,
    ) -> list[str]:
        """
        Creates several research-oriented search queries.

        The original question is preserved. Additional queries
        investigate mechanisms, evidence, limitations, and
        research gaps.
        """

        question = " ".join(
            question.split()
        ).strip()

        if not question:
            return []

        queries = [
            question,
            f"{question} mechanisms",
            f"{question} evidence",
            f"{question} limitations",
            f"{question} research gaps",
        ]

        unique = []
        seen = set()

        for query in queries:
            normalised = query.lower().strip()

            if normalised in seen:
                continue

            seen.add(normalised)
            unique.append(query)

        return unique

    # ---------------------------------------------------------
    # Relevance ranking
    # ---------------------------------------------------------

    @classmethod
    def _relevance_score(
        cls,
        paper: Paper,
        query: str,
    ) -> float:
        """
        Calculates a lightweight retrieval relevance score.

        This is NOT a scientific truth score. It is only used
        to decide which retrieved papers are more closely related
        to the research question.
        """

        query_tokens = cls._tokens(query)

        if not query_tokens:
            return 0.0

        title = paper.title.lower()
        abstract = paper.abstract.lower()

        title_tokens = cls._tokens(
            paper.title
        )

        abstract_tokens = cls._tokens(
            paper.abstract
        )

        title_overlap = (
            len(
                query_tokens
                & title_tokens
            )
            / len(query_tokens)
        )

        abstract_overlap = (
            len(
                query_tokens
                & abstract_tokens
            )
            / len(query_tokens)
        )

        score = (
            title_overlap * 0.65
            + abstract_overlap * 0.35
        )

        normalised_query = (
            " ".join(
                query.lower().split()
            )
        )

        if (
            len(normalised_query) >= 12
            and normalised_query in title
        ):
            score += 0.25

        important_phrases = [
            "scientific discovery",
            "scientific research",
            "research discovery",
            "hypothesis generation",
            "experimental design",
            "knowledge discovery",
            "scientific knowledge",
            "research methodology",
        ]

        for phrase in important_phrases:
            if (
                phrase in normalised_query
                and phrase in title
            ):
                score += 0.10

        return min(
            score,
            1.0,
        )

    @classmethod
    def _rank_papers(
        cls,
        papers: list[Paper],
        queries: list[str],
    ) -> list[Paper]:
        """
        Scores each paper against all research queries and keeps
        the strongest relevance score.
        """

        ranked = []

        for paper in papers:
            scores = [
                cls._relevance_score(
                    paper,
                    query,
                )
                for query in queries
            ]

            paper.relevance = max(
                scores,
                default=0.0,
            )

            ranked.append(paper)

        ranked.sort(
            key=lambda paper: (
                paper.relevance,
                bool(paper.abstract),
                paper.year or 0,
            ),
            reverse=True,
        )

        return ranked

    # ---------------------------------------------------------
    # OpenAlex
    # ---------------------------------------------------------

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

        for item in data.get(
            "results",
            [],
        ):
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
                    title=(
                        item.get("title")
                        or "Untitled"
                    ),
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

    # ---------------------------------------------------------
    # Crossref
    # ---------------------------------------------------------

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
            params["mailto"] = (
                self.crossref_mailto
            )

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

                name = (
                    f"{given} {family}"
                    .strip()
                )

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
                item.get(
                    "abstract",
                    "",
                )
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

    # ---------------------------------------------------------
    # Semantic Scholar
    # ---------------------------------------------------------

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

            doi = external_ids.get(
                "DOI"
            )

            url = item.get("url")

            open_access = item.get(
                "openAccessPdf"
            )

            if (
                open_access
                and open_access.get("url")
            ):
                url = open_access["url"]

            papers.append(
                Paper(
                    title=(
                        item.get("title")
                        or "Untitled"
                    ),
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

    # ---------------------------------------------------------
    # Europe PMC
    # ---------------------------------------------------------

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
                    authors.append(
                        full_name
                    )

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
                    title=(
                        item.get("title")
                        or "Untitled"
                    ),
                    authors=authors,
                    year=self._safe_int(
                        item.get("pubYear")
                    ),
                    doi=doi,
                    url=url,
                    source="Europe PMC",
                    abstract=(
                        item.get(
                            "abstractText"
                        )
                        or ""
                    ),
                )
            )

        return papers

    # ---------------------------------------------------------
    # arXiv
    # ---------------------------------------------------------

    def search_arxiv(
        self,
        query: str,
        limit: int = 10,
    ) -> list[Paper]:

        response = requests.get(
            self.arxiv_url,
            params={
                "search_query": (
                    f"all:{query}"
                ),
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
                href = link.attrib.get(
                    "href"
                )

                if href:
                    url = href
                    break

            doi = None

            identifier = entry.findtext(
                "atom:id",
                default="",
                namespaces=namespace,
            )

            if (
                identifier
                and "doi.org" in identifier
            ):
                doi = (
                    identifier
                    .split(
                        "doi.org/",
                        1,
                    )[-1]
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

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

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

        if (
            not parts
            or not parts[0]
        ):
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

    def _search_source(
        self,
        source: str,
        function,
        queries: list[str],
        limit: int,
    ) -> LiteratureSearchResult:
        """
        Runs several research queries against one source,
        then ranks and deduplicates the results from that source.
        """

        collected = []

        for query in queries:
            result = self._safe_call(
                source=source,
                function=function,
                query=query,
                limit=limit,
            )

            if result.error:
                continue

            collected.extend(
                result.papers
            )

        if not collected:
            return LiteratureSearchResult(
                papers=[],
                source=source,
                error=(
                    "No results returned "
                    "from source."
                ),
            )

        collected = self._deduplicate(
            collected
        )

        collected = self._rank_papers(
            collected,
            queries,
        )

        return LiteratureSearchResult(
            papers=collected[:limit],
            source=source,
        )

    def search_with_status(
        self,
        query: str,
        limit: int = 10,
    ) -> list[LiteratureSearchResult]:
        """
        Performs multi-query, multi-source literature retrieval.

        Each source receives the same research plan, then its
        results are ranked independently.
        """

        queries = self._build_queries(
            query
        )

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
                    self._search_source,
                    source,
                    function,
                    queries,
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

        papers = self._deduplicate(
            papers
        )

        queries = self._build_queries(
            query
        )

        papers = self._rank_papers(
            papers,
            queries,
        )

        return papers

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
                seen_dois.add(
                    doi
                )

            if title:
                seen_titles.add(
                    title
                )

            unique.append(
                paper
            )

        return unique