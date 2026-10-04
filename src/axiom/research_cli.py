import sys

from .axiom import run_research


def main() -> None:

    if len(sys.argv) < 2:
        print(
            'Usage: python -m src.axiom.research_cli '
            '"your research question"'
        )
        raise SystemExit(1)

    question = " ".join(
        sys.argv[1:]
    ).strip()

    if not question:
        print(
            "Research question cannot be empty."
        )
        raise SystemExit(1)

    report = run_research(
        question
    )

    print(
        report.render()
    )


if __name__ == "__main__":
    main()