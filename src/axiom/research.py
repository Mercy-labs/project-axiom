from dataclasses import dataclass

from .knowledge import KnowledgeBase
from .literature import (
    LiteratureSearchResult,
    SafeLiteratureSearcher,
)
from .hypothesis import (
    Hypothesis,
    HypothesisEngine,
)


@dataclass
class ResearchContext:
    question: str
    papers_found: int
    knowledge_summary: str
    hypotheses: list[Hypothesis]
    source_status: list[LiteratureSearchResult]


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

    def investigate(
        self,
        question: str,
    ) -> ResearchContext:

        source_status = (
            self.literature.search_with_status(
                query=question,
                limit=5,
            )
        )

        papers = []

        for result in source_status:
            papers.extend(result.papers)

        self.knowledge.add_papers(
            papers
        )

        context = self.knowledge.context()

        hypotheses = self.hypotheses.generate(
            question=question,
            knowledge_context=context,
        )

        return ResearchContext(
            question=question,
            papers_found=len(
                self.knowledge.papers
            ),
            knowledge_summary=context,
            hypotheses=hypotheses,
            source_status=source_status,
        )