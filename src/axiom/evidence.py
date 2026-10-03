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


class EvidenceExtractor:
    """
    Converts scientific papers into structured evidence
    that Axiom's reasoning engine can inspect.
    """

    def extract(self, papers: list[Paper]) -> list[Evidence]:
        evidence = []

        for paper in papers:
            text = self._paper_text(paper)

            if not text:
                continue

            statements = self._extract_statements(text)

            for statement in statements:
                evidence.append(
                    Evidence(
                        statement=statement,
                        source_title=paper.title,
                        source=paper.source,
                        year=paper.year,
                        strength=self._estimate_strength(statement),
                    )
                )

        return evidence

    @staticmethod
    def _paper_text(paper: Paper) -> str:
        parts = []

        if paper.title:
            parts.append(paper.title)

        if paper.abstract:
            parts.append(paper.abstract)

        return " ".join(parts).strip()

    @staticmethod
    def _extract_statements(text: str) -> list[str]:
        """
        Break paper text into potentially useful evidence statements.
        """

        sentences = re.split(r"(?<=[.!?])\s+", text)

        useful = []

        evidence_terms = {
            "show",
            "shows",
            "found",
            "finds",
            "demonstrate",
            "demonstrates",
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
        }

        for sentence in sentences:
            cleaned = " ".join(sentence.split())

            if len(cleaned) < 40:
                continue

            words = {
                word.strip(".,!?():;[]{}\"'").lower()
                for word in cleaned.split()
            }

            if words.intersection(evidence_terms):
                useful.append(cleaned)

        return useful[:10]

    @staticmethod
    def _estimate_strength(statement: str) -> float:
        """
        Give evidence a conservative initial strength estimate.

        This is not scientific certainty. It is only a signal
        used by Axiom to prioritise evidence.
        """

        strong_terms = {
            "demonstrates",
            "demonstrated",
            "experiment",
            "experimental",
            "results",
            "evidence",
            "found",
        }

        words = {
            word.strip(".,!?():;[]{}\"'").lower()
            for word in statement.split()
        }

        matches = len(words.intersection(strong_terms))

        return round(
            min(0.3 + matches * 0.1, 0.8),
            3,
        )