import numpy as np
from openpyxl import load_workbook
import pandas as pd
from typing import Dict, List, Literal, Generator
from tqdm import tqdm

from .utils import get_target_list

from gtab import BaseTrendSearch


class TrendSearch(BaseTrendSearch):
    def __init__(self,
                 geo: str = "",
                 period: List[str] = ["2016-01-01", "2018-07-31"]):
        super().__init__(geo, period)


    def __col_generator_by_sum(self, names: List[str]) -> Generator[Dict, None, None]:
        """Generate the columns of the excel sheet, transforming the weekly
        frequency data to month through summation.
        """
        curr_year = self.__begin_year
        curr_month = self.__begin_month

        while curr_year < self.__end_year:
            while curr_month <= 12:
                col = []
                for name in names:
                    item = {'year': curr_year, 'month': curr_month, 'name': name}
                    col.append(np.sum(
                        [
                            i['max_ratio']
                            for i in self.collection.find(item)
                        ]
                    ))
                yield {f'{curr_year}_{curr_month}': col}
                curr_month += 1
            curr_year += 1

        curr_month = 1
        while curr_month <= self.__end_month:
            col = []
            for name in names:
                item = {'year': curr_year, 'month': curr_month, 'name': name}
                col.append(np.sum(
                    [
                        i['max_ratio']
                        for i in self.collection.find(item)
                    ]
                ))
            yield {f'{curr_year}_{curr_month}': col}
            curr_month += 1


    def __col_generator_by_mean(self, names: List[str]) -> Generator[Dict, None, None]:
        """Generate the columns of the excel sheet, transforming the weekly
        frequency data to month through taking average.
        """
        curr_year = self.__begin_year
        curr_month = self.__begin_month

        while curr_year < self.__end_year:
            while curr_month <= 12:
                col = []
                for name in names:
                    item = {'year': curr_year, 'month': curr_month, 'name': name}
                    col.append(np.mean(
                        [
                            i['max_ratio']
                            for i in self.collection.find(item)
                        ]
                    ))
                yield {f'{curr_year}_{curr_month}': col}
                curr_month += 1
            curr_year += 1

        curr_month = 1
        while curr_month <= self.__end_month:
            col = []
            for name in names:
                item = {'year': curr_year, 'month': curr_month, 'name': name}
                col.append(np.mean(
                    [
                        i['max_ratio']
                        for i in self.collection.find(item)
                    ]
                ))
            yield {f'{curr_year}_{curr_month}': col}
            curr_month += 1


    def __merge_res(self,
                    df_name: pd.DataFrame,
                    df: pd.DataFrame,
                    raw_data_path: str,
                    sheet_name: str,
                    min_value: float = 0.00001):
        """Retain the old sheet and append non-duplicated columns.
        """

        wb = load_workbook(raw_data_path, read_only=True)
        if sheet_name in wb.sheetnames:
            base_df = (
                pd
                .read_excel(raw_data_path, sheet_name=sheet_name)
                .drop(columns=df_name.columns)
            )
            for col in df.columns:
                if base_df.get('col') is None:
                    base_df[col] = df[col]
            base_df = base_df.reindex(sorted(base_df.columns), axis=1)

            output_df = pd.concat([df_name, base_df], axis=1)
        else:
            output_df = pd.concat([df_name, df], axis=1)

        output_df.replace(0, min_value, inplace=True)
        # with pd.ExcelWriter(path = raw_data_path,
        #                     mode = 'a',
        #                     if_sheet_exists = 'replace'
        #                     ) as writer:
        #
        #     df.to_excel(
        #         writer,
        #         sheet_name = sheet_name,
        #         index = False
        #     )
        return output_df


    def calibrate(self,
                  db_name: str,
                  collection_name: str,
                  continuous_mode: Literal[True, False] = True,
                  max_retry: int = 5,
                  target: Literal['predator', 'victim'] = 'predator',
                  merge_method: Literal['sum', 'mean'] = 'sum',
                  raw_data_path: str = 'data/raw/ victim_list_11222023.xlsx',
                  sheet_name: str = 'Ri_sum_smooth_addmin',
                  min_value: float = 0.00001) -> pd.DataFrame:
        """Calibrate and merge the results, appending/creating a excel sheet.

        Args:
            `db_name`:          name of the database
            `collection_name`:  name of the collection
            `continuous_mode`:  whether to keep calibrate bad keywods which
                fail to calibrate.
            `max_retry`:        maximum round of tries to calibrate bad keywords
            `target`:           whether to calibrate the 'victim' or 'predator'
            `merge_method`:     transforming the data through 'summation' or
                'taking average'
            `raw_data_path`:    the path of the excel
            `sheet_name`:       sheet name for recording calibration results
            `min_value`:        if fail to calibration results, or the trends 
                is smaller than `min_value`), replace them with `min_value`

        Returns:
            None
        """
        names = get_target_list(target)
        self.calibrate_batch(
            names,
            db_name,
            collection_name,
            continuous_mode,
            max_retry
        )
        _df = {}
        match merge_method:
            case 'mean':
                for col in self.__col_generator_by_mean(names):
                    _df = _df | col
            case _:
                for col in self.__col_generator_by_sum(names):
                    _df = _df | col
        df = pd.DataFrame(_df)


        df_name = pd.DataFrame({
            target: names,
            f'{target}_id': [i+1 for i in range(len(names))]
        })
        return self.__merge_res(df_name, df, raw_data_path, sheet_name, min_value)
