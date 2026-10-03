from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class ResearchDataset:
    frame: pd.DataFrame

    def features(self) -> np.ndarray:
        return self.frame[["input"]].to_numpy(dtype=float)

    def targets(self) -> np.ndarray:
        return self.frame["output"].to_numpy(dtype=float)


def build_dataset(
    inputs: list[float],
    outputs: list[float],
) -> ResearchDataset:

    if len(inputs) != len(outputs):
        raise ValueError("Inputs and outputs must have the same length.")

    frame = pd.DataFrame(
        {
            "input": inputs,
            "output": outputs,
        }
    )

    return ResearchDataset(frame=frame)