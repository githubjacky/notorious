from loguru import logger
import numpy as np
import orjson
import pandas as pd
from pathlib import Path
from typing import Optional


def get_target_list(input_path: str = "data/raw/victim_list_01252023.xlsx",
                    sheet: str = "S",
                    target: str = "predator"
                   ):
    """
    Get list of predator or victim
    """
    output_path = Path(f"data/raw/{target}_list.txt")

    if output_path.exists():
        logger.info(f"{target} list has already exists")
        res = [i for i in output_path.read_text().split('\n')][:-1]
    else:
        _res = (
            pd
            .read_excel(input_path, sheet_name=sheet)[target]
            .to_list()
        )
        res = pd.unique(_res).tolist()

        logger.info(f"save the {target} list")
        with output_path.open('w') as f:
            for i in res:
                f.write(i + "\n")

    return res


class MergeUtil:
    def __init__(self,
                 gtab_res_dir: str = 'data/gtab_res/predator/original',
                 raw_data_path: str = 'data/raw/victim_list_01252023.xlsx',
                 ) -> None:
        self.input_paths = list(Path(gtab_res_dir).glob('*/*.json'))
        self.res = {
            i.get('keyword'): i.get('max_ratio')
            for i in [orjson.loads(i.read_text()) for i in self.input_paths]
        }

        self.target = (
            'predator'
            if gtab_res_dir.split('/')[2] == 'predator'
            else
            'victim'
        )
        self.target_list = get_target_list(raw_data_path, target=self.target)


    @property
    def __col_name_freq(self):
        """
        Get the number of observation for each month
        """
        _col_name = [
            '_'.join(i.split('-')[:-1] )
            for i in orjson.loads(self.input_paths[0].read_text()).get('date')
        ]
        freq_dict = {}
        for i in _col_name:
            if i not in freq_dict:
                freq_dict[i] = 1
            else:
                freq_dict[i] += 1

        return freq_dict


    @property
    def merge_by_sum(self):
        data = []
        for idx, i in enumerate(self.target_list):
            beg = 0
            end = 0
            data_i = [i, idx+1]
            for j in self.__col_name_freq.values():
                end += j
                try:
                    data_i.append(np.mean(self.res.get(i)[beg:end]))
                except:
                    data_i.append(None)
                beg = end
            data.append(data_i)

        return data


    @property
    def merge_by_mean(self):
        data = []
        for idx, i in enumerate(self.target_list):
            beg = 0
            end = 0
            data_i = [i, idx+1]
            for j in self.__col_name_freq.values():
                end += j
                try:
                    data_i.append(np.sum(self.res.get(i)[beg:end]))
                except:
                    data_i.append(None)
                beg = end
            data.append(data_i)

        return data


    def raw_merge(self,
              output_data_path: str = 'data/processed/victim_list_01252023.xlsx',
              adjust_method: str = 'sum',
              write: bool = True
              ):
        """
        Merget the gtab result with the first time, which means there is no
        previous results of which should be merged on top.

        param adjust_method: how to transform the weekly data to monthly frequency
        """

        data = (
            self.merge_by_sum
            if adjust_method == 'sum'
            else
            self.merge_by_mean
        )
        df = pd.DataFrame(
            data,
            columns = (
                [self.target, f'{self.target}_id']
                +
                list(self.__col_name_freq.keys()))
            )
        if write:
            sheet = 'Ri' if self.target == 'predator' else 'Rj'
            logger.info(f"add(replace) sheet: new_{sheet}_{adjust_method}")
            with pd.ExcelWriter(output_data_path,
                                mode='a',
                                if_sheet_exists = 'replace'
                                ) as writer:
                df.to_excel(writer, sheet_name = f'new_{sheet}_{adjust_method}', index = False)

        return df


    def concat_merge(self,
                     adjust_method: str = 'sum',
                     write: bool = True,
                     sheet_name: Optional[str] = None
                     ):
        """
        It's not the first time to merge the result, which means the function
        is meant for extending the time period.

        param adjust_method: how to transform the weekly data to monthly frequency
        param sheet_name: which sheet to concat
        """
        pass
