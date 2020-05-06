import pickle


input_files=["data/week1_all_tweets_preprocessing.pkl", "data/week2_all_tweets_preprocessing.pkl",
            "data/week3_all_tweets_preprocessing.pkl", "data/week4_all_tweets_preprocessing.pkl",
            "data/week5_all_tweets_preprocessing.pkl", "data/week6_all_tweets_preprocessing.pkl",
            "data/week7_all_tweets_preprocessing.pkl", "data/week8_all_tweets_preprocessing.pkl",
            "data/week9_all_tweets_preprocessing.pkl", "data/week10_all_tweets_preprocessing.pkl",
]

def extract_data_for_task1_piechart() :
    total_english_tweet_count = 0
    total_non_english_tweet_count = 0
    for file_name in input_files:
        with open(file_name, "rb") as f1:
            all_country_en_dfs, all_langs_non_en_dfs = pickle.load(f1)
            usa_df = all_country_en_dfs['usa']
            uk_df = all_country_en_dfs['uk']
            eu_df = all_country_en_dfs['eu']
            cs_df = all_langs_non_en_dfs['cs']
            da_df = all_langs_non_en_dfs['da']
            et_df = all_langs_non_en_dfs['et']
            fi_df = all_langs_non_en_dfs['fi']
            fr_df = all_langs_non_en_dfs['fr']
            hu_df = all_langs_non_en_dfs['hu']
            nl_df = all_langs_non_en_dfs['nl']
            no_df = all_langs_non_en_dfs['no']
            sv_df = all_langs_non_en_dfs['sv']

            total_english_tweet_count = len(usa_df.index) + len(uk_df.index) + len(eu_df.index) + total_english_tweet_count
            total_non_english_tweet_count = total_non_english_tweet_count + len(cs_df.index) + len(da_df.index) + len(et_df.index) +  len(fi_df.index) + len(fr_df.index) + len(hu_df.index) +  len(nl_df.index) + len(no_df.index) + len(sv_df.index)

    print("total english tweet count is " + str(total_english_tweet_count))
    print("total Non english tweet count is " + str(total_non_english_tweet_count))


def extract_data_for_task1_stackareachart():
    english_tweet_weekly_count = []
    non_english_tweet_weekly_count = []
    for file_name in input_files:
        with open(file_name, "rb") as f1:
            all_country_en_dfs, all_langs_non_en_dfs = pickle.load(f1)
            usa_df = all_country_en_dfs['usa']
            uk_df = all_country_en_dfs['uk']
            eu_df = all_country_en_dfs['eu']
            cs_df = all_langs_non_en_dfs['cs']
            da_df = all_langs_non_en_dfs['da']
            et_df = all_langs_non_en_dfs['et']
            fi_df = all_langs_non_en_dfs['fi']
            fr_df = all_langs_non_en_dfs['fr']
            hu_df = all_langs_non_en_dfs['hu']
            nl_df = all_langs_non_en_dfs['nl']
            no_df = all_langs_non_en_dfs['no']
            sv_df = all_langs_non_en_dfs['sv']
            english_tweet_weekly_count.append(len(usa_df.index) + len(uk_df.index) + len(eu_df.index))
            non_english_tweet_weekly_count.append(len(cs_df.index) + len(da_df.index) + len(et_df.index) +  len(fi_df.index) + len(fr_df.index) + len(hu_df.index) +  len(nl_df.index) + len(no_df.index) + len(sv_df.index))

    print("Weekly english tweet count is ")
    print(english_tweet_weekly_count)

    print("------------------------")

    print("Weekly Non english tweet count is ")
    print(non_english_tweet_weekly_count)


# Extract data for task 2 - Pie chart and Stack Area Chart

def extract_data_for_task_2():
    total_cs_tweet_count = 0
    total_da_tweet_count = 0
    total_et_tweet_count = 0
    total_fi_tweet_count = 0
    total_fr_tweet_count = 0
    total_hu_tweet_count = 0
    total_nl_tweet_count = 0
    total_no_tweet_count = 0
    total_sv_tweet_count = 0

    non_english_weekly_tweets = []

    for file_name in input_files:
        with open(file_name, "rb") as f1:
            all_country_en_dfs, all_langs_non_en_dfs = pickle.load(f1)
            cs_df = all_langs_non_en_dfs['cs']
            da_df = all_langs_non_en_dfs['da']
            et_df = all_langs_non_en_dfs['et']
            fi_df = all_langs_non_en_dfs['fi']
            fr_df = all_langs_non_en_dfs['fr']
            hu_df = all_langs_non_en_dfs['hu']
            nl_df = all_langs_non_en_dfs['nl']
            no_df = all_langs_non_en_dfs['no']
            sv_df = all_langs_non_en_dfs['sv']

            cs_tweet_count = len(cs_df.index)
            da_tweet_count = len(da_df.index)
            et_tweet_count = len(et_df.index) 
            fi_tweet_count = len(fi_df.index) 
            fr_tweet_count = len(fr_df.index) 
            hu_tweet_count = len(hu_df.index) 
            nl_tweet_count = len(nl_df.index) 
            no_tweet_count = len(no_df.index) 
            sv_tweet_count = len(sv_df.index)
            non_english_weekly_tweets.append([cs_tweet_count, da_tweet_count, et_tweet_count, fi_tweet_count, fr_tweet_count, hu_tweet_count, nl_tweet_count, no_tweet_count, sv_tweet_count])

            total_cs_tweet_count = cs_tweet_count + total_cs_tweet_count
            total_da_tweet_count = da_tweet_count + total_da_tweet_count
            total_et_tweet_count = et_tweet_count + total_et_tweet_count
            total_fi_tweet_count = fi_tweet_count + total_fi_tweet_count
            total_fr_tweet_count = fr_tweet_count + total_fr_tweet_count
            total_hu_tweet_count = hu_tweet_count + total_hu_tweet_count
            total_nl_tweet_count = nl_tweet_count + total_nl_tweet_count
            total_no_tweet_count = no_tweet_count + total_no_tweet_count
            total_sv_tweet_count = sv_tweet_count + total_sv_tweet_count

    print("czech - " + str(total_cs_tweet_count))
    print("denmark - " + str(total_da_tweet_count))
    print("estonia - " + str(total_et_tweet_count))
    print("finland - " + str(total_fi_tweet_count))
    print("france - " + str(total_fr_tweet_count))
    print("hungary - " + str(total_hu_tweet_count))
    print("netherlands - " + str(total_nl_tweet_count))
    print("norway - " + str(total_no_tweet_count))
    print("sweden - " + str(total_sv_tweet_count))
    print("Weekly data")
    print(non_english_weekly_tweets)

extract_data_for_task1_piechart()
extract_data_for_task1_stackareachart()
extract_data_for_task_2()




