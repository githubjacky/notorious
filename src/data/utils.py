from loguru import logger
import pandas as pd
from pathlib import Path


def get_predator_list(path: str = "data/raw/victim_list_01252023.xlsx", 
                      sheet: str = "S"
                      ):
    file_name = path.split('/')[-1].split('.')[0]
    output_path = Path(f"data/raw/{file_name}_{sheet}.txt")

    if output_path.exists():
        logger.info("fetch list of predators from existed files")
        res = [
            i
            for i in output_path.read_text().split('\n')
            if i != ''
        ]
    else:
        _res = (
            pd
            .read_excel(path, sheet_name=sheet)["predator"]
            .to_list()
        )
        res = list(set(_res))

        logger.info("save the list of predators")
        with output_path.open('w') as f:
            for i in res:
                f.write(i + "\n")

    return res

