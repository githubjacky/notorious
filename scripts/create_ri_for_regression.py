import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))


import hydra
from omegaconf import DictConfig
from ncls.process import RegUtil


@hydra.main(config_path="../config", config_name="main", version_base=None)
def main(cfg: DictConfig):
    driver = RegUtil(
        cfg.process.s_data_path,
        cfg.process.ri_sheet_name,
        cfg.process.raw_data_path,
    )
    _ = driver.create_ri_for_regression(cfg.process.new_sheet, cfg.process.write)


if __name__ == "__main__":
    main()
