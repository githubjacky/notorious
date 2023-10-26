from loguru import logger
import orjson
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

def merge_all_gtab_res(input_dir: str = 'data/gtab_res/original',
                       raw_data_path: str = 'data/raw/victim_list_01252023.xlsx',
                       adjust_method: str = 'mean',
                       write: bool = True
                      ) -> None:
    input_dir_ = Path(input_dir)
    input_paths = list(input_dir_.glob('*/*.json'))
    _col_name = [
        '_'.join(i.split('-')[:-1] )
        for i in orjson.loads(input_paths[0].read_text()).get('date')
    ]
    col_name_freq = {}
    for i in _col_name:
        if i not in col_name_freq:
            col_name_freq[i] = 1
        else:
            col_name_freq[i] += 1
    _res = [orjson.loads(i.read_text()) for i in input_paths]
    res = {
        i.get('keyword'): i.get('max_ratio') 
        for i in _res
    }

    ri = pd.read_excel(raw_data_path, sheet_name="Ri")
    predators = ri.get('predator').to_list()
    data = []
    match adjust_method:
        case 'mean':
            for idx, i in enumerate(predators):
                beg = 0
                end = 0
                data_i = [i, idx+1]
                for j in col_name_freq.values():
                    end += j
                    data_i.append(np.mean(res.get(i)[beg:end]))
                    beg = end
                data.append(data_i)
        case 'sum':
            for idx, i in enumerate(predators):
                beg = 0
                end = 0
                data_i = [i, idx+1]
                for j in col_name_freq.values():
                    end += j
                    data_i.append(np.sum(res.get(i)[beg:end]))
                    beg = end
                data.append(data_i)


    df = pd.DataFrame(data, columns = ['predator', 'predator_id'] + list(col_name_freq.keys()))
    if write:
        output_data_path: str = 'data/processed/victim_list_01252023.xlsx'
        with pd.ExcelWriter(output_data_path, mode='a') as writer:  
            df.to_excel(writer, sheet_name = f'new_Ri_{adjust_method}', index = False)

    return df