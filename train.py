from pytorch_lightning.cli import LightningCLI
from pytorch_lightning import LightningDataModule
from core.task import MutualInformationEstimator
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import WandbLogger
from typing import Any


class MILightningCLI(LightningCLI):
    def add_arguments_to_parser(self, parser):
        pass

        # there is a bug in argparse that prevents us from using the same argument name twice
        # parser.add_argument('--x_dim', type=int, default=5)
        # parser.link_arguments(
        #     "x_dim",
        #     "model.init_args.proposal.init_args.x_dim", apply_on="parse")
        # parser.link_arguments(
        #     "x_dim",
        #     "model.init_args.ratio_estimator.init_args.x_dim", apply_on="parse")


    # def before_instantiate_classes(self) -> None:
    #     breakpoint()


    def instantiate_trainer(self, **kwargs: Any) -> Trainer:
        # Set the entropy of a and y if the computation is specified in the dataloader
        if hasattr(self.datamodule, "h_a"):
            self.model.h_a = self.datamodule.h_a

        if hasattr(self.datamodule, "h_y"):
            self.model.h_y = self.datamodule.h_y

        trainer = super(MILightningCLI, self).instantiate_trainer(**kwargs)
        if isinstance(trainer.logger, WandbLogger):
            trainer.logger.log_hyperparams(dict(self.config))
        return trainer




def cli_main():
    cli = MILightningCLI(
        MutualInformationEstimator,
        LightningDataModule,
        subclass_mode_model=True,
        subclass_mode_data=True,
        save_config_overwrite=True
    )


if __name__ == "__main__":
    cli_main()