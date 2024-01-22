from loguru import logger
import numpy as np
import orjson
import pandas as pd
from pathlib import Path


from .utils import get_target_list


class MergeUtil:
    def __init__(self,
                 gtab_res_dir: str = 'data/gtab_res/predator/original',
                 geo_period: str = "worldwide_['2016-01-03', '2018-12-31']"
                ) -> None:
        self.input_paths = [
            i
            for i in Path(gtab_res_dir).glob(f'*/*.json')
            if str(i).split('/')[-1] == f"{geo_period}.json"
        ]
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
        self.target_list = get_target_list(self.target)


    @property
    def __col_name_freq(self):
        """Calculate the number of observations in each month."""

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


    def __merge_by_mean(self):
        """Transform query result from the weekly frequncy to monthly frequency."""

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


    def __merge_by_sum(self):
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


    def __merge_res(self, adjust_method):
        """Return the result generated by merging all keyword query results."""

        data = (
            self.__merge_by_sum()
            if adjust_method == 'sum'
            else
            self.__merge_by_mean()
        )
        df = pd.DataFrame(
            data,
            columns = (
                [self.target, f'{self.target}_id']
                +
                list(self.__col_name_freq.keys())
            )
        )
        df.replace(0, 0.00001, inplace=True)

        return df


    def raw_merge(self,
                  adjust_method: str = 'sum',
                  write: bool = True,
                  output_data_path: str = 'data/processed/victim_list_11222023.xlsx'
                 ) -> pd.DataFrame:
        """Merget the gtab result with the first time, which means there is no
        previous results of which should be merged on top.

        Args:
            adjust_method: how to transform the weekly data to monthly frequency

        Returns:
            Pandas DataFrame, which contains the trends of all targets(predator or victim).

        """

        df = self.__merge_res(adjust_method)

        if write:
            sheet = 'Ri' if self.target == 'predator' else 'Rj'
            logger.info(f"add(replace) sheet: new_{sheet}_{adjust_method}")

            with pd.ExcelWriter(path = output_data_path,
                                mode = 'a',
                                if_sheet_exists = 'replace'
                               ) as writer:

                df.to_excel(
                    writer,
                    sheet_name = f'new_{sheet}_{adjust_method}',
                    index = False
                )

        return df


    def concat_merge(self,
                     adjust_method: str = 'sum',
                     write: bool = True,
                     output_data_path: str = 'data/processed/victim_list_11222023.xlsx',
                     sheet_name: str = 'new_Ri_sum_smooth_addmin'
                    ):
        """Make sure it's not the first time to merge the result, which means
        the functio is meant for extending the time period.

        Args:
            adjust_method: how to transform the weekly frequency to monthly
            write: wheter to save dataframe to excel sheet
            sheet_name: which sheet to concat

        Returns:
            Pandas DataFrame, which contains the trends of all targets(predator or victim).
        """
        new_df = self.__merge_res(adjust_method)
        old_df = pd.read_excel(output_data_path, sheet_name)

        cols = new_df.columns[~new_df.columns.isin(old_df.columns)]
        for col in cols:
            old_df[col] = new_df[col]

        if write:
            with pd.ExcelWriter(path = output_data_path,
                                mode = 'a',
                                if_sheet_exists = 'replace'
                               ) as writer:

                old_df.to_excel(
                    writer,
                    sheet_name = sheet_name,
                    index = False
                )

        return old_df
