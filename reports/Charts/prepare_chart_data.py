import pandas as pd
import pickle
from collections import defaultdict


def filter_politician_rows(hashtag, politician_topics):
    if hashtag in politician_topics:
        return True
    return False

politician_topics1 = set(["trump", "democrat", "republican"])
politician_topics2 = set(["democrats", "republicans", "trump"])
politician_topics = set(["democrats", "republicans", "trump"])
coded_countries_v2 = pd.read_csv("InputData/country-coded-nouns-v2.csv")
usa_v2 = coded_countries_v2[coded_countries_v2["Country"] == "usa"]
usa_v2 = usa_v2[usa_v2["#hashtag"].notna()]
usa_topics = set(usa_v2["#hashtag"])
usa_politicians = usa_v2[usa_v2.apply(lambda row: filter_politician_rows(row["#hashtag"], politician_topics), axis=1)]
usa_politicians = usa_politicians[usa_politicians["Synonyms"].notna()]
import ipdb;ipdb.set_trace()
weeks = range(1,11)

weekly_dict = defaultdict(int)
total_dict = defaultdict(int)
total_politicians_dict = defaultdict(int)
weekly_data_list = []
weekly_politician_data_list = []
total_list = []
total_politicians_list = []


for wk in weeks:
    if wk < 8:
        politician_topics = politician_topics1
    else:
        politician_topics = politician_topics2

    print("Processing week{}".format(wk))
    folder = "IntermediateData/week{}/".format(wk)
    filename = folder + "week{}_all_tweets_preprocessing.pkl".format(wk)
    with open(filename, "rb") as f1:
        english_df, _ = pickle.load(f1)
    usa_df = english_df["usa"]
    data_dict = defaultdict(int)
    politcians_dict = defaultdict(int)
    total_politicians_dict = defaultdict(int)
    for idx, row in usa_df.iterrows():

        topics = set()
        if type(row["nhashtag"]) == set:
            topics = row["nhashtag"].intersection(usa_topics)

        for tp in topics:
            data_dict[tp] += 1
            total_dict[tp] += 1
        
        #if type(row["nhashtag"]) == set:
        #    politicians = set()
        #    p_topics = row["nhashtag"].intersection(politician_topics)
        #    if len(p_topics) > 0:
        #        for p_idx, p_row in usa_politicians.iterrows():
        #            if row["tweet_text"].lower().find(p_row["Phrase"]) != -1 or \
        #               row["tweet_text"].lower().find(p_row["Phrase"].replace(" ","")) != -1:
        #                    politicians.add(p_row["Synonyms"])

        #        for person in politicians:
        #            politcians_dict[person] += 1
        #            total_politicians_dict[person] += 1

        #    topics = row["nhashtag"].intersection(usa_topics)

    for key,val in data_dict.items():
        weekly_data_list.append([wk,key,val])

    #for key, val in politcians_dict.items():
    #    weekly_politician_data_list.append([wk, key, val])
    #import ipdb; ipdb.set_trace()

total_tweets = sum(list(total_dict.values()))
#total_politcians_tweets = sum(list(total_politicians_dict.values()))

for key, val in total_dict.items():
    total_list.append([key,val, round(val/total_tweets*100, 2)])

#for key, val in total_politicians_dict.items():
#    total_politicians_list.append([key,val, round(val/total_tweets*100, 2)])

weekly_df = pd.DataFrame(weekly_data_list)
weekly_df.columns = ["Week","Topic","Number_of_tweets"]
weekly_df.to_csv("IntermediateData/chart3_weekly_data.csv")

total_df = pd.DataFrame(total_list)
total_df.columns = ["Topic", "Number_of_tweets", "Percentage"]
total_df.to_csv("IntermediateData/chart3_total_data.csv")

#weekly_politicians_df = pd.DataFrame(weekly_politician_data_list)
#weekly_politicians_df.columns = ["Week","Politician","Number_of_tweets"]
#weekly_politicians_df.to_csv("IntermediateData/chart3_weekly_politicians_data.csv")
#
#total_politicians_df = pd.DataFrame(total_politicians_list)
#total_politicians_df.columns = ["Politician", "Number_of_tweets", "Percentage"]
#total_politicians_df.to_csv("IntermediateData/chart3_total_politicians_data.csv")
