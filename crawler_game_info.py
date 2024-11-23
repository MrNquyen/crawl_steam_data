import numpy as np
import pandas as pd

from bs4 import BeautifulSoup
from collections import deque

import requests
import json
import os
import time
import pickle

'''
    Src: https://medium.com/codex/scraping-information-of-all-games-from-steam-with-python-6e44eb01a299
'''

def read_json(path: str)->dict:
    with open(path, 'r', encoding='utf-8') as file:
        json_dic = json.load(file)
        return json_dic
    

def get_appdetails(
        save_dir_pickle: str,
        save_dir_json: str,
        list_appids_name: str,
        save_dir_game_pickle: str,
        save_dir_error_pickle: str,
    )-> dict:

    # Load pickle
    with open(f'{save_dir_pickle}/{list_appids_name}.p', 'rb') as file:
        list_appids = pickle.load(file)
        appids_deque = deque(list_appids)

    count_ckpt = 0
    error_apps_list = []
    all_game_info = {}
    while len(appids_deque) > 0:
        appid = appids_deque.popleft()
        count_ckpt += 1

        # Request
        proxy = '54.152.3.36:80'
        proxy = '203.150.113.55:57322'
        proxy = '67.43.236.18:1853'
        proxy = '49.156.151.246:83'
        proxies = {
            "http": f'http://{proxy}',
            "https": f'http://{proxy}',
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive"
        }
        try:
            appdetails_req = requests.get(
                f"https://store.steampowered.com/api/appdetails?appids={appid}",
                # proxies=proxies,
                # headers=headers,
                timeout=30,
            )

            if appdetails_req.status_code == 200:
                print(f'>> {count_ckpt}: Request Suggest id {appid}')
                appdetails = appdetails_req.json()
                appdetails = appdetails[str(appid)]
                all_game_info[appid] = appdetails
                time.sleep(4)
            
            elif appdetails_req.status_code == 429:
                print(f'Too many requests. Put App ID {appid} back to deque. Sleep for 10 sec')
                appids_deque.appendleft(appid)
                time.sleep(12)

            elif appdetails_req.status_code == 403:
                print(f'Forbidden to access. Put App ID {appid} back to deque. Sleep for 5 min.')
                appids_deque.appendleft(appid)
                time.sleep(5 * 61)
                continue

            else:
                print("ERROR: status code:", appdetails_req.status_code)
                print(f"Error in App Id: {appid}. Put the app to error apps list.")
                error_apps_list.append(appid)        # error_app_list is a list for storing appids with error
                continue

        except Exception as e:
            print(e)
            print(f'>> {count_ckpt} Load Error appids {appid}')
            # appids_deque.appendleft(appid)
            error_apps_list.append(appid)
            time.sleep(4)

        if count_ckpt % 200 == 0:
                # Dump pickle for checkpoint
                with open(f'{save_dir_pickle}/{list_appids_name}_{count_ckpt}.p', 'wb') as file:
                    pickle.dump(list(appids_deque), file)

                # Dump game_pickle for checkpoint
                with open(f'{save_dir_game_pickle}/{list_appids_name}_{count_ckpt}.p', 'wb') as file:
                    pickle.dump(all_game_info, file)
                    
                # Dump error for checkpoint
                with open(f'{save_dir_error_pickle}/{list_appids_name}_{count_ckpt}_error.p', 'wb') as file:
                    pickle.dump(error_apps_list, file)
    # Dump at end
    ## Dump pickle
    with open(f'{save_dir_pickle}/{list_appids_name}_end.p', 'wb') as file:
        pickle.dump(list(appids_deque), file)

    ## Dump game pickle
    with open(f'{save_dir_game_pickle}/{list_appids_name}_end.p', 'wb') as file:
        pickle.dump(all_game_info, file)

    ## Error list
    with open(f'{save_dir_error_pickle}/err_list_end.p', 'wb') as file:
        pickle.dump(error_apps_list, file)

if __name__=='__main__':
    list_game = read_json('./data/list_game.json')
    list_appids_name = list(list_game.keys())

    get_appdetails(
        save_dir_json='./data/json',
        save_dir_pickle='./data/pickle',
        save_dir_game_pickle='./data/game_pickle',
        list_appids_name='<name>_appids',
        save_dir_error_pickle='./data/error'
    )