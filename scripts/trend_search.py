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
    driver.calibrate(
        cfg.process.db_name,
        cfg.process.collection_name,
        cfg.process.continuous_mode,
        cfg.process.max_retry,
        cfg.process.target,
        cfg.process.merge_method,
        cfg.process.raw_data_path,
        cfg.process.sheet_name,
        cfg.process.min_value
    )


if __name__ == "__main__":
    main()
