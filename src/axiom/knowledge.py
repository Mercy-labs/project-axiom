from dataclasses import dataclass, field
from .literature import Paper


@dataclass
class KnowledgeItem:
    statement: str
    source: str
    evidence_type: str
    confidence: float


@dataclass
class KnowledgeBase:
    papers: list[Paper] = field(default_factory=list)
    findings: list[KnowledgeItem] = field(default_factory=list)

    def add_papers(self, papers: list[Paper]) -> None:
        existing = {
            (paper.title, paper.doi)
            for paper in self.papers
        }

        for paper in papers:
            key = (paper.title, paper.doi)

            if key not in existing:
                self.papers.append(paper)
                existing.add(key)

    def add_finding(
        self,
        statement: str,
        source: str,
        evidence_type: str,
        confidence: float,
    ) -> None:
        self.findings.append(
            KnowledgeItem(
                statement=statement,
                source=source,
                evidence_type=evidence_type,
                confidence=max(0.0, min(1.0, confidence)),
            )
        )

    def context(self) -> str:
        lines = []

        for paper in self.papers[:10]:
            year = paper.year or "unknown year"
            lines.append(
                f"[{paper.source}, {year}] {paper.title}"
            )

        for finding in self.findings[-10:]:
            lines.append(
                f"[{finding.evidence_type}] {finding.statement}"
            )

        return "\n".join(lines)