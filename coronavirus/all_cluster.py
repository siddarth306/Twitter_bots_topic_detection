import pickle
import pandas as pd
from coronavirus.utils import preprocessing
import ast
import demoji
from datasketch import MinHash
import re
from collections import defaultdict

country_map2 = {
    "czech.csv": "czech",
    "denmark.csv": "denmark",
    "estonia.csv": "estonia",
    "finland.csv": "finland",
    "france.csv": "france",
    "hungary.csv": "hungary",
    "netherlands.csv": "netherlands",
    "norway.csv": "norway",
    "Sweden.csv": "sweden",
    "uk.csv": "uk",
}

country_map = {
    "czech.csv": "cs",
    "denmark.csv": "da",
    "estonia.csv": "et",
    "finland.csv": "fi",
    "france.csv": "fr",
    "hungary.csv": "hu",
    "netherlands.csv": "nl",
    "norway.csv": "no",
    "Sweden.csv": "sv",
    "uk.csv": "en"
}

eu_countries = set(["czech",
                    "denmark",
                    "estonia",
                    "finland",
                    "france",
                    "hungary",
                    "netherlands",
                    "norway",
                    "sweden"])

only_en_countries = set(["uk", "usa"])
all_countries = list(only_en_countries) + list(eu_countries) + ["eu"]


def hashtag_filter(hashtag):
    return True if type(hashtag) == str else False


def get_preprocessed_data(tool_config):
    data_df = pd.DataFrame()
    all_country_en_dfs = {}

    phrases_country = {}
    phrases_country_freq = {}
    phrases_hashtag = {}
    nphrases = []

    coded_countries_filename = "coded_countries.csv"
    country_filename = "country-coded-nouns-v2.csv"
    country_filename_v3 = "country-coded-nouns-v3.csv"

    country_phrases_df = pd.read_csv(tool_config["misc_file_loc"].format(
        country_filename_v3))
    coded_country_df = pd.read_csv(tool_config["misc_file_loc"].format(
        coded_countries_filename))

    coded_country_dict = {}
    for idx, row in coded_country_df.iterrows():
        coded_country_dict[row["Phrase"]] = row["Country"]

    for idx, row in country_phrases_df.iterrows():
        nphrases.append(row["Phrase"])
        if type(row["Country"]) == str and len(row["Country"]) > 0:
            phrases_country[row["Phrase"]] = row["Country"]
            phrases_country_freq[row["Phrase"]] = row["Freq"] \
                if type(row["Freq"]) == int \
                else int(row["Freq"].replace(",", ""))
        if type(row["#hashtag"]) == str and len(row["#hashtag"]) > 0:
            phrases_hashtag[row["Phrase"]] = row["#hashtag"]

    print("Preprocessing tweets")

    country_df = pd.read_csv(tool_config["input_file_loc"])

    if len(country_df.index) > 0:
        country_df = preprocessing.tweets_cleaning_coronavirus(
            country_df,
            nphrases,
            phrases_country,
            phrases_country_freq,
            phrases_hashtag,
            eu_countries,
            coded_country_dict)
        data_df = data_df.append(country_df, ignore_index=True)

    for ct in list(only_en_countries) + ["eu"]:
        all_country_en_dfs[ct] = data_df[data_df["ncountry"] == ct]

    return all_country_en_dfs


def remove_wrong_country_tweets(tid, country_tids, all_tids):
    if tid not in country_tids and tid in all_tids:
        return False
    return True


def convert_tids_uids(tid, uid):
    return [int(float(tid)), int(float(uid))]


def save_data(data_df, en, tool_config, country):
    prefix = "en" if en else "non_en"
    clusters_list = []
    tweet_df = data_df
    shares = tweet_df["share_count"].sum() + len(tweet_df.index)
    likes = tweet_df["likes_count"].sum()
    tweet_df = tweet_df.sort_values(by=['likes_count', 'share_count'], ascending=False)
    tweet_text = set()

    tweet_df[["tid", "uid"]] = tweet_df.apply(
        lambda row: pd.Series(convert_tids_uids(row["tid"], row["uid"])), axis=1)
    unique_tweets_map = defaultdict(list)
    unique_links_map = defaultdict(list)
    for idx, row in tweet_df.iterrows():
        tweet_text = row["tweet_text"].lower()
        tweet_text = demoji.replace(row["tweet_text"], "")
        tweet_text = re.sub(r"(https?\://)\S+", "", tweet_text)
        tweet_text = re.sub("RT|,|[\W\d!@#$%&*:\/]*…|\*|&amp;|&gt;|&lt;", "", tweet_text)
        tweet_text = re.sub("[\_\-\«\[\]\(\)\<\>\{\}\»\—\\\@\#\$\%\&\:\/]|[\.]+|[\!]+|[\?]+", "", tweet_text)
        tweet_text_split = tweet_text.lower().split()
        hash_val = MinHash()
        for word in tweet_text_split:
            hash_val.update(word.encode('utf8'))
        min_hash_val = min(hash_val.hashvalues)
        if unique_tweets_map.get(min_hash_val, None) is None:
            unique_tweets_map[min_hash_val] = [None,
                                               row["tweet_text"],
                                               row["tid"],
                                               row["uid"],
                                               set([row["uid"]]),
                                               row["share_count"]+1,
                                               row["likes_count"],
                                               row["timestamp"],
                                               set([tweet_text])]
        else:
            topTweet_obj = unique_tweets_map[min_hash_val]
            topTweet_obj[4].add(row["uid"])
            topTweet_obj[5] += row["share_count"] + 1
            topTweet_obj[6] += row["likes_count"]
            topTweet_obj[8].add(tweet_text)
            
            unique_tweets_map[min_hash_val] = topTweet_obj

        urls = []
        if type(row["url"]) == str:
            try:
                urls_raw = ast.literal_eval(row["url"])
            except (ValueError,TypeError,SyntaxError):
                urls_raw = set(row["url"].split(","))

            urls = []
            if isinstance(urls_raw,set):
                urls = urls_raw
            else:
                for url in urls_raw:
                    urls.append(url["expanded_url"])

        for url in urls:
            try:

                if unique_links_map.get(url, None) is None:
                    unique_links_map[url] = [url,
                                             set([row["uid"]]),
                                             row["share_count"]+1,
                                             row["likes_count"],
                                             row["timestamp"]]
                else:
                    topLink_obj = unique_links_map[url]
                    topLink_obj[1].add(row["uid"])
                    topLink_obj[2] += row["share_count"] + 1
                    topLink_obj[3] += row["likes_count"]
                    unique_links_map[url] = topLink_obj
            except:
                import ipdb;ipdb.set_trace()

    top_tweets_list = list(unique_tweets_map.values())
    top_tweets_list.sort(key=lambda elem: (elem[6], elem[5], len(elem[4])), reverse=True)
    print("Tweet clusters count: {}".format(len(top_tweets_list)))
    top_tweets_list = top_tweets_list[:50]
    for tweet_idx in range(len(top_tweets_list)):
        top_tweets_list[tweet_idx][4] = len(top_tweets_list[tweet_idx][4])
        top_tweets_list[tweet_idx][8] = len(top_tweets_list[tweet_idx][8])

    top_links_list = list(unique_links_map.values())
    top_links_list.sort(key=lambda elem: (elem[3], elem[2], len(elem[1])), reverse=True)
    top_links_list = top_links_list[:50]
    for tweet_idx in range(len(top_links_list)):
        top_links_list[tweet_idx][1] = len(top_links_list[tweet_idx][1])

    bot_count = len(tweet_df["uid"].unique())
    tweet_number = len(tweet_df.index)
    tweet_text = list(tweet_text)

    clusters_list.append([["corona virus", "covid 19"],
                          ["corona-virus"],
                          likes,
                          shares,
                          bot_count,
                          tweet_number,
                          top_tweets_list,
                          top_links_list])


    clusters_list.sort(key=lambda elem: (elem[2],elem[3], elem[4]), reverse=True)
    for c_idx in range(len(clusters_list)):
        clusters_list[c_idx] = [tool_config["date"][0],
                                tool_config["date"][1],
                                "Topic " + str(c_idx)] + clusters_list[c_idx]
    if len(clusters_list) > 0:
        clusters_df = pd.DataFrame(clusters_list)
        clusters_df.columns = ["Start date",
                               "End date",
                               "Topic Number",
                               "Keywords",
                               "Hashtags",
                               "Likes Count",
                               "Shares Count",
                               "Bot Count",
                               "Tweets Count",
                               "Top Tweets",
                               "Top Links"]
        filename = "{}_{}_{}_topic_clusters.csv".format(
            tool_config["week_str"],
            country, prefix)
        clusters_df.to_csv(tool_config["result_file_loc"].format(filename),
                           index=False)
    return []


def calculate_clusters(tool_config):

    if tool_config["week"] >= 13 and tool_config["week"] <= 15:
        try:
            filename = tool_config["week_str"] + "_all_coronvirus_tweets_preprocessing.pkl"
            with open(tool_config["inter_file_loc"].format(filename), "rb") as f1:
                all_country_en_dfs = pickle.load(f1)
        except FileNotFoundError:

            filename = tool_config["week_str"] + "_all_tweets_preprocessing.pkl"
            with open(tool_config["inter_file_loc"].format(filename), "rb") as f1:
                all_country_en_dfs = pickle.load(f1)

            corona_phrases_dict = {}
            phrases_df = pd.read_csv(tool_config["misc_file_loc"].format(
                "coronavirus-nouns-v3.csv"))
            for idx, row in phrases_df.iterrows():
                corona_phrases_dict[row["Phrase"]] = row["Country"] if type(row["Country"]) == "str" else "na"

            for key, df in all_country_en_dfs.items():
                print("Processing {}".format(key))
                data = all_country_en_dfs[key]
                all_country_en_dfs[key] = data[data.apply(
                    lambda row: preprocessing.filter_tweets_coronavirus(
                        row["tweet_text"], corona_phrases_dict, row["country"]),
                    axis=1)]
                all_country_en_dfs[key]["share_count"] = all_country_en_dfs[key].apply(
                    preprocessing.calc_shares_coronavirus,
                    axis=1)
                all_country_en_dfs[key]["likes_count"] = all_country_en_dfs[key].apply(
                    preprocessing.calc_likes_coronavirus,
                    axis=1)
            filename = tool_config["week_str"] + "_all_coronvirus_tweets_preprocessing.pkl"
            with open(tool_config["inter_file_loc"].format(filename), "wb") as f1:
                pickle.dump(all_country_en_dfs, f1)

    
        for key, val_df in all_country_en_dfs.items():
            print("Saving {} data".format(key))
            if len(val_df) > 0:
                save_data(val_df, True, tool_config, key)
 
    else:

        filename = tool_config["week_str"] + "_all_tweets_preprocessing.pkl"
        try:
            with open(tool_config["inter_file_loc"].format(filename), "rb") as f1:
                all_country_en_dfs = pickle.load(f1)
            print("Using tweets intermediate file")

        except FileNotFoundError:
            all_country_en_dfs = get_preprocessed_data(tool_config)
            with open(tool_config["inter_file_loc"].format(filename), "wb") as f1:
                pickle.dump(all_country_en_dfs, f1)

        for key, val_df in all_country_en_dfs.items():
            if len(val_df) > 0:
                save_data(val_df, True, tool_config, key)

    return []
