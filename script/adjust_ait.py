import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

from src.data.utils import adjust_ait
import argparse


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        '--input_data_path',
        type = str,
        default = 'data/processed/victim_list_modified_robert.xlsx'
    )
    args.add_argument(
        '--predator_victim_sheet',
        type = str,
        default = '名單'
    )
    args.add_argument(
        '--ait_csv_path',
        type = str,
        default = 'data/raw/ait.csv'
    )
    args.add_argument(
        '--write',
        action = 'store_true',
    )
    args.add_argument(
        '--sum',
        action = 'store_true',
    )

    return args.parse_args()


if __name__ == "__main__":
    args = parse_args()
    adjust_ait(
        args.input_data_path,
        args.predator_victim_sheet,
        args.ait_csv_path,
        args.write,
        args.sum
    )
