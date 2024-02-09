from loguru import logger
import numpy as np
import pandas as pd
from time import strptime


def adjust_ait(input_data_path = 'data/processed/victim_list_10302023.xlsx',
               predator_victim_sheet = '名單',
               sum = False
              ):
    df_date = pd.read_excel(input_data_path, sheet_name = predator_victim_sheet)
    victim2date = {
        df_date.iloc[i]['victim']: df_date.iloc[i]['time']
        for i in range(len(df_date))
    }

    predator2victim = {}
    for i in range(len(df_date)):
        predator = df_date.iloc[i]['predator']
        victim = df_date.iloc[i]['victim']
        if predator not in predator2victim:
            predator2victim[predator] = [victim]
        else:
            predator2victim[predator].append(victim)

    victim2predator = {
        df_date.iloc[i]['victim']: df_date.iloc[i]['predator']
        for i in range(len(df_date))
    }

    victim2friend = {}
    for victim in victim2predator.keys():
        predator = victim2predator[victim]
        possible_friends = predator2victim[predator]
        victim2friend[victim] = []
        for i in possible_friends:
            if i != victim: victim2friend[victim].append(i)

    df_a = pd.read_excel(input_data_path, 'S')
    interval = [
        pd.to_datetime(f'20{i[3:5]}-{strptime(i[:3],"%b").tm_mon}', format = '%Y-%m') 
        for i in df_a.columns 
        if i not in ['predator', 'predator_id', 'victim', 'victim_id ']
    ]
    victim2id = {
        df_a.iloc[i]['victim']: df_a.iloc[i]['victim_id '] - 1
        for i in range(len(df_a))
    }

    victim2friend_id = {
        victim: list(map(lambda x: victim2id[x], victim2friend[victim]))
        for victim in victim2friend.keys()
    }

    s = np.zeros((len(victim2date.keys()), len(interval)))
    for idx_i, victim in enumerate(victim2date.keys()):
        issue_date = victim2date[victim]
        for idx_j, date in enumerate(interval):
            if date > issue_date:
                s[idx_i][idx_j] = 1
            elif date.year == issue_date.year and date.month == issue_date.month:
                s[idx_i][idx_j] = 1

    s_adjust = np.zeros((len(victim2date.keys()), len(interval)))
    for idx_i, victim in enumerate(victim2date.keys()):
        if len(victim2friend_id[victim]) != 0:
            for id in victim2friend_id[victim]:
                s_adjust[idx_i] += s[id]

    new_sheet_name = 'adjust_ait'
    if sum:
        new_sheet_name = 'sum_adjust_ait'
        logger.info(f'new sheet: {new_sheet_name}')

        victim2section = {
            df_date.iloc[i]['victim']: df_date.iloc[i]['section']
            for i in range(len(df_date))
        }
        section2victim_id = {}
        for i in range(len(df_date)):
            section = df_date.iloc[i]['section']
            victim = df_date.iloc[i]['victim']
            if section not in section2victim_id:
                section2victim_id[section] = [victim2id[victim]]
            else:
                section2victim_id[section].append(victim2id[victim])

        victim2section_friend_id = {}
        for victim in victim2predator.keys():
            section = victim2section[victim]
            possible_friends = section2victim_id[section]

            victim2section_friend_id[victim] = []
            for i in possible_friends:
                if i not in victim2friend_id[victim] and i != victim2id[victim]:
                    victim2section_friend_id[victim].append(i)

        for idx_i, victim in enumerate(victim2date.keys()):
            if len(victim2section_friend_id[victim]) != 0:
                for id in victim2section_friend_id[victim]:
                        s_adjust[idx_i] += s[id]

    df_a_adjust = pd.DataFrame({
        'predator': df_a['predator'],
        'predaotr_id': df_a['predator_id'],
        'victim': df_a['victim'],
        'victim_id': df_a['victim_id ']
    })


    for idx, i in enumerate(interval):
        df_a_adjust[i] = [i[idx] for i in s_adjust]

    with pd.ExcelWriter(input_data_path,
                        mode='a',
                        if_sheet_exists = 'replace'
                        ) as writer:
        df_a_adjust.to_excel(writer, sheet_name = new_sheet_name, index = False)

    return df_a_adjust

