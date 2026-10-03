import numpy as np
import torch
from torch import nn


class NeuralResearchModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU(),
            nn.Linear(16, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class NeuralTrainer:
    def __init__(self, epochs: int = 200, learning_rate: float = 0.01):
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.model = NeuralResearchModel()

    def fit(
        self,
        inputs: np.ndarray,
        targets: np.ndarray,
    ) -> None:

        x = torch.tensor(
            inputs,
            dtype=torch.float32,
        ).reshape(-1, 1)

        y = torch.tensor(
            targets,
            dtype=torch.float32,
        ).reshape(-1, 1)

        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.learning_rate,
        )

        loss_function = nn.MSELoss()

        self.model.train()

        for _ in range(self.epochs):
            optimizer.zero_grad()

            prediction = self.model(x)
            loss = loss_function(prediction, y)

            loss.backward()
            optimizer.step()

    def predict(self, value: float) -> float:
        self.model.eval()

        x = torch.tensor(
            [[value]],
            dtype=torch.float32,
        )

        with torch.no_grad():
            prediction = self.model(x)

        return float(prediction.item())