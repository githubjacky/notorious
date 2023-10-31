import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

from src.data.utils import merge_all_gtab_res
import argparse


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        '--input_dir',
        type = str,
        default = 'data/gtab_res/predator/original'
    )
    args.add_argument(
        '--raw_data_path',
        type = str,
        default = 'data/raw/victim_list_01252023.xlsx'
    )
    args.add_argument(
        '--output_data_path',
        type = str,
        default = 'data/processed/victim_list_10302023 copy.xlsx'
    )
    args.add_argument(
        '--adjust_method',
        type = str,
        default = 'mean'
    )
    args.add_argument(
        '--write',
        action = 'store_true',
    )

    return args.parse_args()


if __name__ == "__main__":
    args = parse_args()
    merge_all_gtab_res(
        args.input_dir,
        args.raw_data_path,
        args.output_data_path,
        args.adjust_method,
        args.write
    )
