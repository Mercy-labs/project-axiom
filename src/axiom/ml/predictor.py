from dataclasses import dataclass
import numpy as np
from sklearn.ensemble import RandomForestRegressor


@dataclass
class Prediction:
    value: float
    uncertainty: float


class MLPredictor:
    def __init__(self, random_state: int = 42):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=random_state,
        )
        self.trained = False

    def fit(
        self,
        features: np.ndarray,
        targets: np.ndarray,
    ) -> None:

        if len(features) < 2:
            raise ValueError("At least two observations are required.")

        self.model.fit(features, targets)
        self.trained = True

    def predict(self, features: np.ndarray) -> Prediction:
        if not self.trained:
            raise RuntimeError("Predictor must be trained first.")

        trees = np.array(
            [
                tree.predict(features)[0]
                for tree in self.model.estimators_
            ]
        )

        return Prediction(
            value=float(np.mean(trees)),
            uncertainty=float(np.std(trees)),
        )