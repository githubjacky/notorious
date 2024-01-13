import datetime
from functools import cached_property
from loguru import logger
import orjson
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm
import sys

from .gtab.core import GTAB
from .negative_search import NegativeKW_Collector


class TrendSearch():
    def __init__(self,
                 target_list: List[str],
                 suffix: str = "Sexual harassment",
                 geo: str = "",
                 period: List[str] = ["2016-01-01", "2018-07-31"],
                 n_url: int = 20,
                 search_sleep: int = 10,
                 sentiment_model: str = "sentiment",
                 extract_model: str = "Voicelab/vlt5-base-keywords"
                 ):
        self.invalid_keyword_path = Path('env/invalid_keyword.txt')
        self.invalid_keywords = (
            self.invalid_keyword_path
            .read_text()
            .split('\n')
        )[:-1]

        self.keyword_list = (
            [
                i + " " + "\"" + suffix + "\""
                for i in target_list
            ]
            if suffix is not None
            else
            list(set(target_list))
        )

        self.geo = geo
        self.period = period
        self.suffix = suffix if suffix is not None else "original"

        self.n_url = n_url
        self.search_sleep = search_sleep
        self.sentiment_model = sentiment_model
        self.extract_model = extract_model.split('/')[1]

        self.bad_keywords = []


    @cached_property
    def collector(self):
        return NegativeKW_Collector(
            self.n_url,
            self.search_sleep,
            self.sentiment_model,
            self.extract_model
        )


    def setup(self, init_path: str = "gtab_config"):
        """
        Setup GTAB class for scraping google trends.
        """
        timeframe = " ".join(self.period)
        anchor_dir = Path(f"{init_path}/output/google_anchorbanks")
        anchor_file = "_".join((
            f"google_anchorbank_geo={self.geo}",
            f"timeframe={timeframe}.tsv"
        ))
        anchor_path = anchor_dir / anchor_file

        t = GTAB(dir_path=init_path)
        if not anchor_path.exists():
            t.set_options(
                pytrends_config={
                    "geo": self.geo,
                    "timeframe": timeframe
                },
                conn_config={"backoff_factor": 1.0}
            )
            t.create_anchorbank()

        t.set_active_gtab(anchor_file)
        self.t = t


    def negative_search(self, target: str):
        """
        Try to find a valid negative suffix, if we can't collect trend using
        such keyword(keyword = suffix + name).

        :param target: is the name of either 'predator' or 'victim'
        """
        self.collector.setup(target)
        output_path = (
            self.collector.output_dir 
            /
            "_".join((
                self.extract_model,
                self.sentiment_model,
                str(self.collector.n_url),
                "keywords.json"
            ))
        )
        if output_path.exists():
            logger.info("negative search: keywords exists, fetch from the file")
            keywords = [
                i
                for i in orjson.loads(output_path.read_text())["keywords"]
            ]
        else:
            keywords = self.collector.fetch_keywords(output_path)

        return keywords


    def calibrate_instance(self, keyword: str):
        try:
            return self.t.new_query(keyword).get('max_ratio')
        except:
            raise KeyError("invalid keyword")


    @staticmethod
    def __merge_res(base_date, add_date, base_max_ratio, add_max_ratio):
        insert_date = add_date[0]
        insert_pos = 0
        for t, date in enumerate(base_date):
            if date >= insert_date:
                insert_pos = t
                break

        merge_date = base_date[:insert_pos] + add_date
        merge_max_ratio = base_max_ratio[:insert_pos] + add_max_ratio


        return  merge_date, merge_max_ratio


    def calibrate_and_write(self,
                            keyword: str,
                            output_path: Path,
                            prev_max_ratio: Optional[List],
                            prev_date: Optional[List],
                            continuous_mode = True
                            ):
        status = 0
        try:
            logger.info(f"query: {keyword}")
            res = self.calibrate_instance(keyword)
        except ConnectionError as e:
            logger.warning(f"{e}: {keyword}")
            sys.exit()
        except KeyError as e:
            logger.info(f"{e}: Can't get trend result-{keyword}")
            status = -1

        if status == 0:
            target_date = [i.date() for i in res.index]
            target_max_ratio = res.tolist()

            if prev_max_ratio is not None and prev_date is not None:
                if prev_date[0] <= target_date[0]:
                    logger.info(f"merge {str(prev_date[0])}-{str(prev_date[-1])} with {str(target_date[0])}-{str(target_date[-1])}")
                    target_date, target_max_ratio = self.__merge_res(
                        prev_date, target_date, prev_max_ratio, target_max_ratio
                    )
                else:
                    logger.info(f"merge {str(target_date[0])}-{str(target_date[-1])} with {str(prev_date[0])}-{str(prev_date[-1])}")
                    target_date, target_max_ratio = self.__merge_res(
                        target_date, prev_date, target_max_ratio, prev_max_ratio
                    )

            with output_path.open('wb') as f:
                f.write(orjson.dumps(
                    {
                        "keyword": keyword,
                        "date": target_date,
                        "max_ratio": target_max_ratio
                    },
                    option = orjson.OPT_INDENT_2
                ))
        else:
            if continuous_mode:
                self.bad_keywords.append(keyword)
            else:
                with self.invalid_keyword_path.open('a') as f:
                    f.write(keyword + '\n')

        return status


    @cached_property
    def __begin_date(self):
        return datetime.datetime.strptime(self.period[0], '%Y-%m-%d').date()


    @cached_property
    def __end_date(self):
        return datetime.datetime.strptime(self.period[1], '%Y-%m-%d').date()


    def __check_merge(self, output_dir: Path, geo: str):
        """
        Check whether to merge with previous results, and if merge, return
        previous results, including the max_ratio and date
        """
        prev_res_path = [str(i) for i in list(output_dir.glob('*.json'))]
        empty = (
            True
            if len(prev_res_path) == 0
            else
            False
        )

        output_path_name = ""
        prev_date = None
        prev_max_ratio = None

        if not empty:
            merge_period = datetime.timedelta(days=0)
            for f in prev_res_path:

                prev_geo = f.split('/')[-1].split('_')[0]
                if prev_geo == geo:
                    prev_res = orjson.loads(Path(f).read_text())
                    _prev_date = [
                        datetime.datetime.strptime(i, "%Y-%m-%d").date()
                        for i in prev_res['date']
                    ]

                    merge = True
                    if (
                        _prev_date[0].month == self.__begin_date.month and
                        _prev_date[-1].month == self.__end_date.month
                    ):
                        merge = False
                    elif (
                        _prev_date[0].month <= self.__begin_date.month and
                        _prev_date[-1].month >= self.__end_date.month
                    ):
                        merge = False
                    elif (
                        _prev_date[0].month >= self.__begin_date.month and
                        _prev_date[-1].month <= self.__end_date.month
                    ):
                        merge = False

                    if merge:
                        start_period = (
                            _prev_date[0]
                            if _prev_date[0] <= self.__begin_date
                            else
                            self.__begin_date
                        )
                        end_period = (
                            _prev_date[-1]
                            if _prev_date[-1] >= self.__end_date
                            else
                            self.__end_date
                        )
                        delta = end_period - start_period

                        if delta > merge_period:
                            output_path_name = f"{geo}_{[str(start_period), str(end_period)]}.json"
                            prev_max_ratio = prev_res['max_ratio']
                            prev_date = _prev_date
                            merge_period = delta

        return output_path_name, prev_max_ratio, prev_date

    def __continuous_calibrate(self, result_dir, geo):
        i = 1
        while len(self.bad_keywords) != 0:
            keywords = self.bad_keywords.copy()
            self.bad_keywords = []

            for keyword in tqdm(keywords, position=i):
                target = keyword.split(' "')[0]
                output_dir = (
                result_dir
                    /
                    f"{self.suffix}/{target}"
                )
                output_dir.mkdir(parents=True, exist_ok=True)
                _output_path_name, prev_max_ratio, prev_date = self.__check_merge(output_dir, geo)
                output_path = (
                    output_dir / _output_path_name
                    if _output_path_name != ""
                    else
                    output_dir / f"{geo}_{self.period}.json"
                )

                _ = self.calibrate_and_write(
                    keyword,
                    output_path,
                    prev_max_ratio,
                    prev_date,
                    True
                )
            i += 1


    def calibrate_batch(self,
                        sleep: float = 5.,
                        fetch_keyword = True,
                        result_dir: Path = Path(f"data/gtab_res/predator"),
                        continuous_mode = True
                        ) -> None:
        logger.remove()
        log_info = Path("log/gtab_info.log")
        log_warn = Path("log/gtab_warn.log")
        if log_info.exists(): log_info.unlink(missing_ok=True)
        if log_warn.exists(): log_warn.unlink(missing_ok=True)

        logger.add(log_info, level='INFO')
        logger.add(log_warn, level='WARNING')

        geo = "worldwide" if self.geo == "" else self.geo

        self.t.set_options(gtab_config = {"sleep": sleep})
        for keyword in tqdm(self.keyword_list, position = 0):
            target = keyword.split(' "')[0]
            output_dir = (
                result_dir
                /
                f"{self.suffix}/{target}"
            )
            output_dir.mkdir(parents=True, exist_ok=True)
            _output_path_name, prev_max_ratio, prev_date = self.__check_merge(output_dir, geo)
            output_path = (
                output_dir / _output_path_name
                if _output_path_name != ""
                else
                output_dir / f"{geo}_{self.period}.json"
            )

            if not output_path.exists():
                status = self.calibrate_and_write(
                    keyword,
                    output_path,
                    prev_max_ratio,
                    prev_date,
                    continuous_mode
                )

                if status == -1 and fetch_keyword:
                    negative_keywords = self.negative_search(target)
                    i = 0
                    while status == -1 and i < len(negative_keywords):

                        new_keyword = f'{target} "{negative_keywords[i]}"'
                        status = self.calibrate_and_write(
                            new_keyword,
                            output_path,
                            prev_max_ratio,
                            prev_date,
                            continuous_mode
                        )
                        i += 1

                    if status == -1:
                        logger.warning(f"fail to collect trend: {target}")
                        with Path('env/no_result.txt').open('a') as f:
                            f.write(target + '\n')
                    else:
                        with Path('env/check_result.txt').open('a') as f:
                            f.write(f"{target}: {negative_keywords[i-1]}" + '\n')
                elif status == 0:
                    with Path('env/valid_result.txt').open('a') as f:
                        f.write(target + '\n')
            else:
                logger.info(f"calibrate result has already existed: {keyword}")

        if continuous_mode:
            self.__continuous_calibrate(result_dir, geo)
