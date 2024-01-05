import argparse
from loguru import logger
import pandas as pd


def create_ri_for_regression(input_path: str = 'data/processed/victim_list_10302023.xlsx',
                             predator_victim_info: str = 'S', 
                             ri:str = 'new_Ri_sum_smooth',
                             new_sheet: str = 'new_Ri_for_regression',
                             write = True
                            ):
    logger.info(input_path)
    df_predator_victim = pd.read_excel(
        input_path, 
        sheet_name = predator_victim_info
    )
    df_ri =  pd.read_excel(input_path, sheet_name = ri)

    df = pd.DataFrame({
        'predator': df_predator_victim['predator'],
        'predaotr_id': df_predator_victim['predator_id'],
        'victim': df_predator_victim['victim'],
        'victim_id': df_predator_victim['victim_id ']
    })

    predator2freq = {}
    for i in range(len(df)):
        predator = df.iloc[i]['predator']
        if  predator not in predator2freq:
            predator2freq[predator] = [0]
        else:
            predator2freq[predator][0] += 1

    target_cols = df_ri.columns.drop(['predator', 'predator_id'])
    for col in target_cols:
        predaotr2ri = {
            df_ri.iloc[i]['predator']: df_ri.iloc[i][col]
            for i in range(len(df_ri))
        }
        df[col] = [
            predaotr2ri[predator]
            for predator in df['predator']
        ]
        
    if write:
        with pd.ExcelWriter(input_path,
                            mode='a',
                            if_sheet_exists = 'replace'
                            ) as writer:
            df.to_excel(writer, sheet_name = new_sheet, index = False)

    return df


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        '--input_path',
        type = str,
        default = 'data/processed/victim_list_modified_robert.xlsx'
    )
    args.add_argument(
        '--predator_victim_info',
        type = str,
        default = 'S'
    )
    args.add_argument(
        '--ri',
        type = str,
        default = 'new_Ri_sum_smooth'
    )
    args.add_argument(
        '--new_sheet',
        type = str,
        default = 'new_Ri_for_regression'
    )
    args.add_argument(
        '--write',
        action = 'store_true',
    )

    return args.parse_args()


if __name__ == "__main__":
    args = parse_args()
    create_ri_for_regression(
        args.input_path,
        args.predator_victim_info,
        args.ri,
        args.new_sheet,
        args.write
    )
