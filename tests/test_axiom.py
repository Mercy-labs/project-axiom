from src.axiom.experiment import Experiment, SimulationEngine
from src.axiom.ml.dataset import build_dataset
from src.axiom.ml.predictor import MLPredictor
from src.axiom.verification import Verifier


def test_simulation_produces_observation():
    engine = SimulationEngine()

    observation = engine.run(
        Experiment(
            input_value=2,
            name="test",
        )
    )

    assert isinstance(observation.output_value, float)


def test_dataset_creation():
    dataset = build_dataset(
        [1, 2, 3],
        [2, 4, 6],
    )

    assert list(dataset.frame.columns) == [
        "input",
        "output",
    ]

    assert len(dataset.frame) == 3


def test_ml_predictor():
    dataset = build_dataset(
        [1, 2, 3, 4],
        [2, 4, 6, 8],
    )

    predictor = MLPredictor()

    predictor.fit(
        dataset.features(),
        dataset.targets(),
    )

    prediction = predictor.predict([[5]])

    assert isinstance(prediction.value, float)
    assert prediction.uncertainty >= 0


def test_verification_requires_evidence():
    verifier = Verifier()

    result = verifier.verify(
        observation_count=1,
        evidence_strength=0.9,
    )

    assert result.verified is False