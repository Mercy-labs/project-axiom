# Project Axiom

Project Axiom is a long-term research project exploring AI systems for autonomous scientific discovery.

## Vision

Axiom is designed around a research loop:

Research question
        ↓
Scientific literature
        ↓
Knowledge
        ↓
Hypotheses
        ↓
Experiments
        ↓
Observations
        ↓
Machine learning
        ↓
Next experiment
        ↓
Evaluation
        ↓
Verification
        ↓
Research memory
        ↓
New research cycle

## Current architecture

### Scientific research

Axiom can query scholarly metadata from OpenAlex and Crossref.

### Knowledge

Research sources are kept separate from Axiom-generated experimental findings.

### Hypotheses

Axiom generates competing hypotheses instead of assuming one answer.

### Experiments

The current environment contains a deterministic computational simulation.

This simulation is a development environment and must not be treated as a real physical scientific discovery.

### Machine learning

Axiom currently contains:

- NumPy
- Pandas
- scikit-learn
- PyTorch

The machine-learning layer can learn from previous computational observations and help select subsequent experiments.

### Verification

Axiom separates an experimental result from a verified conclusion.

### Memory

Research cycles can be stored for later analysis.

## Important scientific principle

Axiom should never confuse:

- published scientific evidence
- computational observations
- model predictions
- hypotheses
- verified conclusions

These are different levels of evidence.

## API layer

External API credentials are supplied through environment variables.

Never place API keys directly in source code.

Supported variables include:

AXIOM_API_URL
AXIOM_API_KEY

## Running locally

Install dependencies:

    pip install -r requirements.txt

Run tests:

    python -m pytest tests -q

Run Axiom:

    python -m src.axiom.axiom

## Project direction

The long-term goal is to develop systems capable of:

1. identifying research questions
2. studying existing scientific knowledge
3. generating hypotheses
4. designing experiments
5. learning from experimental results
6. selecting subsequent experiments
7. evaluating evidence
8. verifying conclusions
9. remembering previous research
10. proposing new research directions

Physical laboratory experimentation requires appropriate equipment, supervision, safety controls, and human oversight. The computational system does not independently perform physical experiments.