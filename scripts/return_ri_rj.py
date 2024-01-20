import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

import hydra
from omegaconf import DictConfig

from ncls.process import MergeUtil


@hydra.main(config_path="../config", config_name="main", version_base=None)
def main(cfg: DictConfig):
    driver = MergeUtil(cfg.process.gtab_res_dir, cfg.process.geo_period)
    match cfg.process.merge_method:
        case 'raw':
            _ = driver.raw_merge(
                cfg.process.adjust_method,
                cfg.process.write,
                cfg.process.output_data_path,
            )
        case 'concat':
            _ = driver.concat_merge(
                cfg.process.adjust_method,
                cfg.process.write,
                cfg.process.output_data_path,
                cfg.process.concat_sheet_name
            )


if __name__ == "__main__":
    main()
