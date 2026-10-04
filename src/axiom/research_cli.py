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

    print(
        "=== AXIOM RESEARCH STARTED ==="
    )
    print(
        f"Question: {question}"
    )
    print()

    print(
        "Running literature research..."
    )

    report = run_research(
        question
    )

    print(
        f"Research result type: {type(report).__name__}"
    )

    if report is None:
        print(
            "ERROR: run_research() returned None."
        )
        raise SystemExit(1)

    print(
        "Rendering research report..."
    )

    rendered = report.render()

    print(
        f"Rendered result type: {type(rendered).__name__}"
    )

    if rendered is None:
        print(
            "ERROR: report.render() returned None."
        )
        raise SystemExit(1)

    print()
    print(
        rendered
    )


if __name__ == "__main__":
    main()