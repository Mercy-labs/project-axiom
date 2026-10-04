from dataclasses import dataclass
import re

from .literature import Paper


@dataclass
class Evidence:
    statement: str
    source_title: str
    source: str
    year: int | None
    strength: float
    relevance: float = 0.0


class EvidenceExtractor:
    """
    Extracts and ranks evidence from scientific literature.

    The scores are research heuristics, not scientific truth values.
    """

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
        "about",
        "into",
        "their",
        "they",
        "them",
        "than",
        "can",
        "may",
        "be",
    }

    EVIDENCE_TERMS = {
        "show",
        "shows",
        "found",
        "finds",
        "demonstrate",
        "demonstrates",
        "demonstrated",
        "suggest",
        "suggests",
        "indicate",
        "indicates",
        "results",
        "result",
        "evidence",
        "discover",
        "discovery",
        "improve",
        "improves",
        "increase",
        "increases",
        "decrease",
        "decreases",
        "performance",
        "experiment",
        "experimental",
        "model",
        "system",
        "study",
        "studies",
        "analysis",
        "observed",
        "identified",
        "predict",
        "prediction",
    }

    def extract(
        self,
        papers: list[Paper],
        question: str = "",
    ) -> list[Evidence]:

        evidence = []

        for paper in papers:
            text = self._paper_text(
                paper
            )

            if not text:
                continue

            statements = (
                self._extract_statements(
                    text
                )
            )

            for statement in statements:
                relevance = (
                    self._relevance(
                        question,
                        statement,
                    )
                )

                strength = (
                    self._estimate_strength(
                        statement
                    )
                )

                evidence.append(
                    Evidence(
                        statement=statement,
                        source_title=paper.title,
                        source=paper.source,
                        year=paper.year,
                        strength=strength,
                        relevance=relevance,
                    )
                )

        evidence.sort(
            key=lambda item: (
                item.relevance,
                item.strength,
            ),
            reverse=True,
        )

        return evidence

    @staticmethod
    def _paper_text(
        paper: Paper,
    ) -> str:

        parts = []

        if paper.title:
            parts.append(
                paper.title
            )

        if paper.abstract:
            parts.append(
                paper.abstract
            )

        return " ".join(
            parts
        ).strip()

    def _extract_statements(
        self,
        text: str,
    ) -> list[str]:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        useful = []

        for sentence in sentences:
            cleaned = " ".join(
                sentence.split()
            )

            if len(cleaned) < 50:
                continue

            words = self._words(
                cleaned
            )

            if words.intersection(
                self.EVIDENCE_TERMS
            ):
                useful.append(
                    cleaned
                )

        return useful[:12]

    def _relevance(
        self,
        question: str,
        statement: str,
    ) -> float:

        question_words = self._words(
            question
        )

        statement_words = self._words(
            statement
        )

        if not question_words:
            return 0.0

        overlap = (
            question_words
            .intersection(
                statement_words
            )
        )

        return round(
            min(
                len(overlap)
                / max(
                    len(question_words),
                    1,
                ),
                1.0,
            ),
            3,
        )

    @classmethod
    def _words(
        cls,
        text: str,
    ) -> set[str]:

        words = {
            word.strip(
                ".,!?():;[]{}\"'"
            ).lower()
            for word in text.split()
        }

        return {
            word
            for word in words
            if (
                word
                and word not in cls.STOP_WORDS
                and len(word) > 2
            )
        }

    @classmethod
    def _estimate_strength(
        cls,
        statement: str,
    ) -> float:

        words = cls._words(
            statement
        )

        strong_terms = {
            "demonstrates",
            "demonstrated",
            "experiment",
            "experimental",
            "results",
            "evidence",
            "found",
            "identified",
            "observed",
            "analysis",
        }

        moderate_terms = {
            "suggests",
            "suggest",
            "indicates",
            "indicate",
            "study",
            "studies",
            "model",
            "prediction",
        }

        strong_matches = len(
            words.intersection(
                strong_terms
            )
        )

        moderate_matches = len(
            words.intersection(
                moderate_terms
            )
        )

        score = (
            0.25
            + strong_matches * 0.08
            + moderate_matches * 0.04
        )

        return round(
            min(score, 0.85),
            3,
        )