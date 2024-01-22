import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

import hydra
from loguru import logger
from omegaconf import DictConfig
from pathlib import Path
from ncls.process import TrendSearch


@hydra.main(config_path="../config", config_name="main", version_base=None)
def main(cfg: DictConfig):
    geo = "" if cfg.process.gtab.geo == "worldwide" else cfg.process.gtab.geo
    logger.info(f"district: {geo}")

    driver = TrendSearch(
        cfg.process.gtab.target,
        cfg.process.gtab.suffix,
        geo,
        cfg.process.gtab.period,
        cfg.process.negative_search.n_url,
        cfg.process.negative_search.sleep,
        cfg.process.negative_search.sentiment_model,
        cfg.process.negative_search.extract_model
    )
    driver.setup(cfg.process.gtab.init_path)
    driver.calibrate_batch(
        cfg.process.gtab.sleep,
        cfg.process.gtab.fetch_keyword,
        Path(cfg.process.gtab.gtab_res_dir) / cfg.process.gtab.target,
        cfg.process.gtab.continuous_mode
    )


if __name__ == "__main__":
    main()
