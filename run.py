from models import binary, multiclass, regression
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from pytorch_lightning.logging import TestTubeLogger
from utils.logger import make_directory
from utils.args import parse_args
from utils.set_seed import set_random_seed

MODELS = {"binary": binary.BinaryModel,
          "multiclass": multiclass.MulticlassModel,
          "regression": regression.RegressionModel}


def run(arch, loader):
    set_random_seed(2434)
    args = parse_args()
    device = list(range(args.device))
    save_dir = make_directory(args.logdir)

    model = MODELS[args.task](arch, loader, args)

    exp = TestTubeLogger(save_dir=save_dir)
    exp.log_hyperparams(args)

    early_stop = EarlyStopping(
        monitor='avg_val_loss',
        patience=args.stop_num,
        verbose=False,
        mode='min')

    checkpoint = ModelCheckpoint(
        filepath=save_dir / "checkpoint",
        save_best_only=True,
        verbose=False,
        monitor='avg_val_loss',
        mode='min')

    backend = None if len(device) == 1 else "dp"

    trainer = Trainer(
        logger=exp,
        max_nb_epochs=args.epoch,
        checkpoint_callback=checkpoint,
        early_stop_callback=early_stop,
        gpus=device,
        distributed_backend=backend)

    trainer.fit(model)
    print("##### training finish #####")

    trainer.test(model)
    print("##### test finish #####")