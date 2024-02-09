import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))


import hydra
from omegaconf import DictConfig
from src.process import adjust_ait


@hydra.main(config_path="../config", config_name="main", version_base=None)
def main(cfg: DictConfig):
    _ = adjust_ait(
        cfg.process.raw_data_path,
        cfg.process.predator_victim_sheet,
        cfg.process.sum
    )


if __name__ == "__main__":
    main()
