from dataclasses import dataclass

from .knowledge import KnowledgeBase
from .literature import (
    SafeLiteratureSearcher,
    Paper,
)
from .hypothesis import (
    HypothesisEngine,
    Hypothesis,
)
from .evidence import (
    EvidenceExtractor,
    Evidence,
)
from .reasoner import (
    AxiomReasoner,
    ReasoningResult,
)


@dataclass
class ResearchContext:
    question: str
    papers_found: int
    knowledge_summary: str
    hypotheses: list[Hypothesis]
    evidence: list[Evidence]
    reasoning: ReasoningResult
    source_status: list


class ScientificResearcher:
    def __init__(
        self,
        literature_searcher: SafeLiteratureSearcher,
        knowledge_base: KnowledgeBase,
        hypothesis_engine: HypothesisEngine,
    ):
        self.literature = literature_searcher
        self.knowledge = knowledge_base
        self.hypotheses = hypothesis_engine
        self.evidence_extractor = (
            EvidenceExtractor()
        )
        self.reasoner = AxiomReasoner()

    def investigate(
        self,
        question: str,
    ) -> ResearchContext:

        search_results = (
            self.literature.search_with_status(
                query=question,
                limit=10,
            )
        )

        papers = []
        source_status = []

        for result in search_results:
            papers.extend(
                result.papers
            )
            source_status.append(
                result
            )

        papers = (
            self.literature._deduplicate(
                papers
            )
        )

        self.knowledge.add_papers(
            papers
        )

        context = self.knowledge.context()

        evidence = (
            self.evidence_extractor.extract(
                papers=papers,
                question=question,
            )
        )

        reasoning_evidence = []

        for item in evidence:
            reasoning_evidence.append(
                (
                    f"{item.source} — "
                    f"{item.statement}"
                )
            )

        reasoning = self.reasoner.reason(
            question=question,
            evidence=reasoning_evidence,
        )

        return ResearchContext(
            question=question,
            papers_found=len(papers),
            knowledge_summary=context,
            hypotheses=[],
            evidence=evidence,
            reasoning=reasoning,
            source_status=source_status,
        )