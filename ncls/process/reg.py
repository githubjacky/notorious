import pandas as pd


class RegUtil:
    def __init__(self,
                 s_data_path: str = 'data/raw/s.csv',
                 ri_sheet_name: str= 'new_Ri_sum_smooth_addmin',
                 raw_data_path: str = 'data/raw/11222023.xlsx'
                ):
        df = pd.read_csv(s_data_path)
        self.df_ri = pd.read_excel(raw_data_path, sheet_name=ri_sheet_name)
        self.raw_data_path = raw_data_path

        predator2id = {
            self.df_ri.iloc[i]['predator']: self.df_ri.iloc[i]['predator_id']
            for i in range(len(self.df_ri))
        }
        self.df = pd.DataFrame({
            'predator': df['predator'],
            'predator_id': [predator2id[df.iloc[i]['predator']] for i in range(len(df))],
            'victim': df['victim'],
            'victim_id': range(1, len(df)+1)
        })

    def create_ri_for_regression(self,
                                 new_sheet: str = 'new_Ri_for_regression',
                                 write = True
                                ):
        months = self.df_ri.columns.drop(['predator', 'predator_id'])
        for month in months:
            predaotr2ri = {
                self.df_ri.iloc[i]['predator']: self.df_ri.iloc[i][month]
                for i in range(len(self.df_ri))
            }
            self.df[month] = [
                predaotr2ri[predator]
                for predator in self.df['predator']
            ]

        if write:
            with pd.ExcelWriter(self.raw_data_path,
                                mode='a',
                                if_sheet_exists = 'replace'
                                ) as writer:
                self.df.to_excel(writer, sheet_name = new_sheet, index = False)

        return self.df

