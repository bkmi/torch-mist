from typing import Tuple, Type, Optional, Dict, Any

import torch
import numpy as np
import pandas as pd
from torch.optim import Optimizer
from collections.abc import Iterator
from tqdm.auto import tqdm
from torch.optim import Adam

from torch_mist.estimators.base import MutualInformationEstimator



def optimize_mi_estimator(
        estimator: MutualInformationEstimator,
        dataloader: Iterator[Tuple[torch.Tensor, torch.Tensor]],
        n_epochs: int = 1,
        optimizer_class: Type[Optimizer] = Adam,
        optimizer_params: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:

    opt_params = {"params": estimator.parameters()}

    if optimizer_params is None:
        optimizer_params = {"lr": 5e-4}

    opt_params.update(optimizer_params)
    
    opt = optimizer_class(
        [opt_params]
    )

    log = []
    iteration = 0

    for epoch in range(n_epochs):
        for x, y in tqdm(dataloader):
            estimation = estimator(x, y)
            loss = estimator.loss(x, y)

            log.append(
                {
                    'value': estimation.item(),
                    'loss': loss.item(),
                    'iteration': iteration,
                }
            )
            iteration += 1

            opt.zero_grad()
            loss.backward()
            opt.step()

    return pd.DataFrame(log)


def estimate_mi(
        estimator: MutualInformationEstimator,
        dataloader: Iterator[Tuple[torch.Tensor, torch.Tensor]],
) -> Tuple[float, float]:
    mis = []

    for x, y in dataloader:
        estimation = estimator(x, y)
        mis.append(estimation.item())

    return np.mean(mis), np.std(mis)
