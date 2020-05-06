import time
import csv
from tqdm import tqdm
import pandas as pd
import multiprocessing
import pickle
import urllib.request
import demoji


def expand_urls(urls):
    request_base = "https://b6dkeerw62x81o1j.pro.urlex.org/json/"

    request_payload = "***".join(urls)
    new_request_payload = demoji.replace(request_payload)
    request_url = request_base + new_request_payload
    
    try:
        with urllib.request.urlopen(request_url) as response:
            data = response.read()
            return data
    except:
        return request_url


def check():
    with urllib.request.urlopen("https://b6dkeerw62x81o1j.pro.urlex.org/json/https://b6dkeerw62x81o1j.pro.urlex.org/json/https://t.co/YbiSKfyrUi***https://t.co/TprCVapaTw***https://t.co/RS8pSeiiBz***https://t.co/EqtVo2u0i8***https://t.co/gXOkxcDbed***https://t.co/Y12ZwFkHto***https://t.co/pekkbfmqHa***https://t.co/Jj1Xq80yHY***https://t.co/tC47YZO2et") as response:
        data = response.read()
        print(data)


def get_cpu_count():
    cpu_count = multiprocessing.cpu_count()
    if cpu_count > 30:
        cpu_count = 30
    elif cpu_count >= 10:
        cpu_count = 8
    elif cpu_count >= 8:
        cpu_count = 7
    elif cpu_count == 4:
        cpu_count = 3
    else:
        cpu_count = 2

    return cpu_count


def get_urls():
    urls = pd.read_csv("shortened_urls.csv")
    return urls["urls"].values


def main():
    start_time = time.time()

    urls = get_urls()
    max_len = len(urls)
    intervals = []

    for idx in range(0, len(urls), 10):
        if idx + 9 < max_len:
            intervals.append((idx, idx+9))
        else:
            intervals.append((idx, max_len))

    expand_urls_list = []

    pool = multiprocessing.Pool(processes=1)
    results = [pool.apply_async(expand_urls, args=(urls[idx[0]:idx[1]],)) for idx in intervals]
    for result in tqdm(results):
        expand_urls_list.append(result.get())
    pool.close()
    pool.terminate()
    pool.join()
    
    with open("expanded_url.pkl", "wb") as file:
        pickle.dump(expand_urls_list, file)
       
    print(expand_urls_list)

    execution_time = time.time() - start_time
    print("-------------------------------------")
    print("EXECUTION TIME FOR MAIN:" + str(time.strftime("%H:%M:%S", time.gmtime(execution_time))))
    print("-------------------------------------")


main()
# check()
