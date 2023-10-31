import os, sys
sys.path.append(os.path.abspath(f"{os.getcwd()}"))

from src.data.utils import create_ri_for_regression
import argparse


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        '--input_path',
        type = str,
        default = 'data/processed/victim_list_10302023.xlsx'
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
