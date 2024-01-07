import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

import hydra
from omegaconf import DictConfig
from pathlib import Path

from src.data.trend_search import TrendSearch
from src.data.utils import get_target_list


@hydra.main(config_path="../config", config_name="main", version_base=None)
def main(cfg: DictConfig):
    geo = "" if cfg.process.gtab.geo == "worldwide" else cfg.process.gtab.geo

    engine = TrendSearch(
        get_target_list(
            cfg.process.gtab.s_path,
            cfg.process.gtab.target
        ),
        cfg.process.gtab.suffix,
        geo,
        cfg.process.gtab.period,
        cfg.process.negative_search.n_url,
        cfg.process.negative_search.sleep,
        cfg.process.negative_search.sentiment_model,
        cfg.process.negative_search.extract_model
    )
    engine.setup(cfg.process.gtab.init_path)
    engine.calibrate_batch(
        cfg.process.gtab.sleep,
        cfg.process.gtab.fetch_keyword,
        Path(cfg.process.gtab.gtab_res_dir),
        cfg.process.gtab.continuous_mode
    )


if __name__ == "__main__":
    main()
