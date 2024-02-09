import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))


import hydra
from omegaconf import DictConfig
from src.process import TrendSearch


@hydra.main(config_path="../config", config_name="main", version_base=None)
def main(cfg: DictConfig):
    driver = TrendSearch(
        cfg.process.geo if cfg.process.geo is not None else "",
        cfg.process.period
    )
    driver.setup(cfg.process.init_path)


if __name__ == "__main__":
    main()
