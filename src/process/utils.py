from loguru import logger
import pandas as pd
from pathlib import Path


def get_target_list(target: str = "predator"):
    """Get list of predators or victims."""

    output_path = Path(f"data/raw/{target}_list.txt")

    if output_path.exists():
        logger.info(f"{target} list has already exists")
        res = [i for i in output_path.read_text().split('\n')][:-1]
    else:
        res = pd.unique(pd.read_csv('data/raw/s.csv')[target]).tolist()

        with output_path.open('w') as f:
            for i in res:
                f.write(i + "\n")
        logger.info(f"save the {target} list to {output_path}")

    return res


