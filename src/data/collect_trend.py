from gtab import GTAB
import hydra
from loguru import logger
from omegaconf import DictConfig
from pathlib import Path
from typing import List
import pandas as pd
from tqdm import tqdm
import sys


class TrendSearch():
    def __init__(self, 
                 predator_list: List[str], 
                 suffix: str = "Sexual harassment",
                geo: str = "", 
                period: List[str] = ["2016-01-01", "2018-07-31"]
                 ):
        invalid_keywords = (
            Path('env/invalid_keyword.txt')
            .read_text()
            .split('\n')
        )[:-1]

        keyword_list = [
            i + " " + "\"" + suffix + "\""
            for i in list(set(predator_list))
        ]

        self.keyword_list = [
            i
            for i in keyword_list
            if i not in invalid_keywords
        ]

        self.geo = geo
        self.period = period
        self.suffix = suffix


    def setup(self, 
              init_path: str = "gtab_config", 
              ):

        anchor_dir = Path(f"{init_path}/output/google_anchorbanks")
        anchor_file = "_".join((
            f"google_anchorbank_geo={self.geo}",
            f"timeframe={self.period[0]} {self.period[1]}.tsv"
        ))
        anchor_path = anchor_dir / anchor_file

        t = GTAB(dir_path=init_path)
        if not anchor_path.exists():
            t.set_options(pytrends_config={
                "geo": "",
                "time_frame": " ".join(self.period)
            })
            t.create_anchorbank()

        t.set_active_gtab(anchor_file)
        self.t = t

    def calibrate_instance(self, keyword: str):
        return (
            self.t
            .new_query(keyword)['max_ratio']
            .resample('M')
            .sum()
        )

    def calibrate_batch(self, 
                        output_dir: str = "data/gtab_res", 
                        sleep: float = 1.,
                        retry: int = 3
                        ):
        logger.remove()
        log_info = Path("log/gtab_info.log")
        log_warn = Path("log/gtab_warn.log")
        if log_info.exists(): log_info.unlink(missing_ok=True)
        if log_warn.exists(): log_warn.unlink(missing_ok=True)

        logger.add(log_info, level='INFO')
        logger.add(log_warn, level='WARNING')

        geo = "worldwide" if self.geo == "" else self.geo
        result_dir = Path(f"{output_dir}/{self.suffix}/{geo}_{self.period}")
        result_dir.mkdir(parents=True, exist_ok=True)

        self.t.set_options(
            gtab_config = {"sleep": sleep},
            # conn_config = {"proxies": ["https://"]}
        )
        for keyword in tqdm(self.keyword_list):
            logger.info(f"query: {keyword}")
            output_path = result_dir / f"{keyword}.csv"
            if not output_path.exists():
                try:
                    res = self.calibrate_instance(keyword)
                    res.to_csv(output_path)
                except ConnectionError as e:
                    # self.t.set_options(
                    #     conn_config={"proxies": ["https://"]}
                    # )
                    logger.warning(f"429 error: {keyword}")
                    sys.exit()
                except TypeError:
                    logger.warning(f"-1 error: {keyword}")
                except:
                    i = 1
                    while i <= retry: 
                        try:
                            res = self.calibrate_instance(keyword)
                            res.to_csv(result_dir / f"{keyword}.csv")
                            break
                        except:
                            logger.info(f"retry for {i} times for querying {keyword}")
                            i += 1
                    logger.warning(f"error: {keyword}")
            else:
                logger.info(f"query result has alread exist: {keyword}")


def get_predator_list(path: str = "data/raw/victim_list_01252023.xlsx", 
                      sheet: str = "S"
                      ):
    return (
        pd
        .read_excel(path, sheet_name=sheet)["predator"]
        .to_list()
    )

    
@hydra.main(config_path="../../config", config_name="main", version_base=None)
def main(cfg: DictConfig):
    geo = "" if cfg.gtab.geo == "worldwide" else cfg.gtab.geo

    engine = TrendSearch(
        get_predator_list(cfg.gtab.keyword_path, cfg.gtab.sheet),
        cfg.gtab.suffix,
        geo,
        cfg.gtab.period
    )
    engine.setup(cfg.gtab.init_path)
    engine.calibrate_batch(cfg.gtab.output_dir, cfg.gtab.sleep, cfg.gtab.retry)


if __name__ == "__main__":
    main()
