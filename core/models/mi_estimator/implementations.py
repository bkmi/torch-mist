from typing import Optional, List

from torch.distributions import Distribution
from pyro.distributions import ConditionalDistribution

from core.models.proposal import TransformedNormalProposal
from core.models.ratio import SeparableRatioEstimatorMLP
from core.models.ratio.base import RatioEstimator
from core.models.ratio.joint import JointRatioEstimatorMLP
from core.models.baseline.base import Baseline, ConstantBaseline, BatchLogMeanExp, ExponentialMovingAverage, \
    LearnableMLPBaseline, TUBABaseline, InterpolatedBaseline
from core.models.mi_estimator.base import MutualInformationEstimator


class BA(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            transform_name: str = "conditional_linear",
            **kwargs

    ):
        proposal = TransformedNormalProposal(
            x_dim=x_dim,
            y_dim=y_dim,
            hidden_dims=hidden_dims,
            transform_name=transform_name
        )

        super().__init__(
            proposal=proposal,
            **kwargs
        )


class NWJ(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            neg_samples: int = 1,
            **kwargs

    ):
        ratio_estimator = JointRatioEstimatorMLP(
            x_dim=x_dim,
            y_dim=y_dim,
            hidden_dims=hidden_dims,
        )

        super().__init__(
            ratio_estimator=ratio_estimator,
            baseline=ConstantBaseline(1.0),
            neg_samples=neg_samples,
            **kwargs
        )


class MINE(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            neg_samples: int = 1,
            ratio_estimator: Optional[RatioEstimator] = None,
            **kwargs
    ):
        if ratio_estimator is None:
            ratio_estimator = JointRatioEstimatorMLP(
                x_dim=x_dim,
                y_dim=y_dim,
                hidden_dims=hidden_dims,
            )

        super().__init__(
            ratio_estimator=ratio_estimator,
            baseline=BatchLogMeanExp(dim=2),
            grad_baseline=ExponentialMovingAverage(gamma=0.9),
            neg_samples=neg_samples,
            **kwargs
        )


class InfoNCE(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            **kwargs
    ):
        ratio_estimator = SeparableRatioEstimatorMLP(
            x_dim=x_dim,
            y_dim=y_dim,
            hidden_dims=hidden_dims,
        )

        super().__init__(
            ratio_estimator=ratio_estimator,
            baseline=BatchLogMeanExp(dim=1),
            neg_samples=0,  # 0 signifies the whole batch is used as negative samples
            **kwargs
        )


class JS(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            neg_samples: int = 1,
            **kwargs
    ):
        ratio_estimator = JointRatioEstimatorMLP(
            x_dim=x_dim,
            y_dim=y_dim,
            hidden_dims=hidden_dims,
        )

        super().__init__(
            ratio_estimator=ratio_estimator,
            baseline=ConstantBaseline(1.0),
            js_grad=True,
            neg_samples=neg_samples,
            **kwargs
        )


class TUBA(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            baseline_hidden_dims: Optional[List[int]] = None,
            neg_samples: int = 1,
            **kwargs
    ):
        if baseline_hidden_dims is None:
            baseline_hidden_dims = hidden_dims

        ratio_estimator = JointRatioEstimatorMLP(
            x_dim=x_dim,
            y_dim=y_dim,
            hidden_dims=hidden_dims,
        )

        baseline = LearnableMLPBaseline(
            x_dim=x_dim,
            hidden_dims=baseline_hidden_dims,
        )

        super().__init__(
            ratio_estimator=ratio_estimator,
            baseline=baseline,
            neg_samples=neg_samples,
            **kwargs
        )


class AlphaTuba(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            baseline_hidden_dims: Optional[List[int]] = None,
            alpha: float = 0.5,
            neg_samples: int = 1,
            **kwargs,
    ):
        if baseline_hidden_dims is None:
            baseline_hidden_dims = hidden_dims

        ratio_estimator = JointRatioEstimatorMLP(
            x_dim=x_dim,
            y_dim=y_dim,
            hidden_dims=hidden_dims,
        )

        baseline_1 = BatchLogMeanExp()
        baseline_2 = LearnableMLPBaseline(x_dim, baseline_hidden_dims)

        baseline = InterpolatedBaseline(
            baseline_1=baseline_1,
            baseline_2=baseline_2,
            alpha=alpha
        )

        super().__init__(
            ratio_estimator=ratio_estimator,
            baseline=baseline,
            neg_samples=neg_samples,
            **kwargs,
        )


class SMILE(MutualInformationEstimator):
    def __init__(
            self,
            x_dim: int,
            y_dim: int,
            hidden_dims: List[int],
            tau: float = 5.0,
            neg_samples: int = 1,
            **kwargs
    ):
        ratio_estimator = JointRatioEstimatorMLP(
            x_dim=x_dim,
            y_dim=y_dim,
            hidden_dims=hidden_dims,
        )

        super().__init__(
            ratio_estimator=ratio_estimator,
            baseline=BatchLogMeanExp(dim=2),
            js_grad=True,
            tau=tau,
            neg_samples=neg_samples,
            **kwargs
        )

