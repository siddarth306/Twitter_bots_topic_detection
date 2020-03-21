import pickle
import pandas as pd
from collections import defaultdict, namedtuple
from utils import preprocessing
from utils import clustering
import numpy as np
import ast
import demoji
from datasketch import MinHash
import re
import json
import urllib.request

country_map2 = {"czech.csv": "czech",
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
country_map = {"czech.csv": "cs",
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
eu_countries = set(["czech", "denmark", "estonia", "finland", "france", "hungary", "netherlands", "norway", "sweden"])
only_en_countries = set(["uk","usa"])
all_countries = list(only_en_countries) + list(eu_countries) + ["eu"]

def hashtag_filter(hashtag):
    return True if type(hashtag) == str else False


def get_preprocessed_data(tool_config):
    data_df = pd.DataFrame()
    non_en_data_df = pd.DataFrame()
    all_country_en_dfs = {}
    all_langs_non_en_dfs = {}

    phrases_country = {}
    phrases_country_freq = {}
    phrases_hashtag = {}
    nphrases = []
    country_filename = "country-coded-nouns-v2.csv"
    coded_countries_filename = "coded_countries.csv"
    country_phrases_df = pd.read_csv(tool_config["input_out_file_loc"].format(country_filename))
    coded_country_df = pd.read_csv(tool_config["input_out_file_loc"].format(coded_countries_filename))
    
    coded_country_dict = {}
    for idx, row in coded_country_df.iterrows():
        coded_country_dict[row["Phrase"]] = row["Country"]

    for idx, row in country_phrases_df.iterrows():
        nphrases.append(row["Phrase"])
        if type(row["Country"]) == str and len(row["Country"]) > 0:
            phrases_country[row["Phrase"]] = row["Country"]
            phrases_country_freq[row["Phrase"]] = row["Freq"] if type(row["Freq"]) == int else int(row["Freq"].replace(",",""))
        if type(row["#hashtag"]) == str and len(row["#hashtag"]) > 0:
            phrases_hashtag[row["Phrase"]] = row["#hashtag"]

    #nphrases.sort(key= lambda x: x[1], reverse=True)

    
    print("Preprocessing tweets")
    for file_n in [*country_map.keys()]:
        print("Processing " + file_n)
        country_df = pd.read_csv(tool_config["input_file_loc"].format(file_n))
        
        if country_map2[file_n] not in only_en_countries:
            country_non_en_df = country_df[country_df["language"] != "en"]
            if len(country_non_en_df.index) > 0:
                country_non_en_df = preprocessing.tweets_cleaning(country_non_en_df,
                                                                  nphrases,
                                                                  phrases_country,
                                                                  phrases_country_freq,
                                                                  phrases_hashtag,
                                                                  eu_countries,
                                                                  coded_country_dict, False)
                non_en_data_df = non_en_data_df.append(country_non_en_df, ignore_index = True)

        country_df = country_df[country_df["language"]=="en"]
        if len(country_df.index) > 0:
            country_df = preprocessing.tweets_cleaning(country_df,
                                                       nphrases,
                                                       phrases_country,
                                                       phrases_country_freq,
                                                       phrases_hashtag,
                                                       eu_countries,
                                                       coded_country_dict)
            data_df = data_df.append(country_df, ignore_index = True)
            country_df = country_df[country_df.apply(lambda row: hashtag_filter(row["hashtags"]), axis=1)]

    for ct in list(only_en_countries) + ["eu"]:
        all_country_en_dfs[ct] = data_df[data_df["ncountry"] == ct]

    languages = list(non_en_data_df["language"].unique())
    for lang in languages:
        all_langs_non_en_dfs[lang] = non_en_data_df[non_en_data_df["language"] == lang]

    #preprocessed_data = preprocessing.topic_preprocessing(data_df)

    return all_country_en_dfs, all_langs_non_en_dfs

def remove_wrong_country_tweets(tid, country_tids, all_tids):
    if tid not in country_tids and tid in all_tids:
        return False
    return True

def save_hashtag_clusters(clusters, topic_preprocessed, data_df, en, tool_config, country, urls_map, urls_set):
    prefix = "en" if en else "non_en"
    clusters_list = []
    n = 0
    max_share_count = max_freq_count = 0
    min_share_count = min_freq_count = 9223372036854775807
    phrase_tf_ihf = topic_preprocessed["phrases_tf_ihf"]
    hashtags_phrases = topic_preprocessed["hashtags_phrases"]
    phrases_shares= topic_preprocessed["phrases_shares"]
    phrases_freq= topic_preprocessed["phrases_freq"]
    phrases_tweets = topic_preprocessed["phrases_tweets"]
    hashtags_shares = topic_preprocessed["hashtags_shares"]
    hashtags_freq = topic_preprocessed["hashtags_freq"]
    if len(topic_preprocessed["hashtags"]) < 500: 
        p_limit = 4
    else:
        p_limit = 7
    for idx, ctr in enumerate(clusters):
        phrases = set()
        tweet_tids = set()
        for ht in ctr:
            for ph in hashtags_phrases[ht]:
                if phrase_tf_ihf.get(ph, None) is None:
                    tf_score = -1
                else:
                    tf_score = phrase_tf_ihf[ph]
                share_count = phrases_shares[ph]
                freq_count = phrases_freq[ph]
                phrases.add((ph,tf_score, phrases_shares[ph], phrases_freq[ph]))
        if len(phrases) > p_limit:

            
            phrases_list = list(phrases)
            phrases_list.sort(key=lambda x: (x[1], x[2], x[3]), reverse= True)
            clean_phrases = [i[0] for i in phrases_list[:10]]
            for ph in phrases_list:
                tweet_tids = tweet_tids.union(phrases_tweets[ph[0]])
            
            tweet_df = data_df[data_df['tid'].isin(list(tweet_tids))]
            shares = tweet_df["share_count"].sum() + len(tweet_df.index)
            likes = tweet_df["likes_count"].sum()
            bot_set = set()
            tweet_df = tweet_df.sort_values(by=['likes_count', 'share_count'], ascending=False)
            tweet_text = set()
            links = []

            #topTweet = namedtuple('TopTweet', 'hash_obj tweet_text tid uid bot_count share_count like_count')
            #topLink = namedtuple('TopLink', 'link bot_count share_count like_count')
            unique_tweets_map = defaultdict(list)
            unique_links_map = defaultdict(list)
            for idx, row in tweet_df.iterrows():
                text_urls = re.findall("(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", row["tweet_text"])
                tweet_text = demoji.replace(row["tweet_text"],"")
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
                                                       int(row["tid"]),
                                                       int(row["uid"]),
                                                       set([row["uid"]]),
                                                       row["share_count"]+1,
                                                       row["likes_count"]]
                else:
                    topTweet_obj = unique_tweets_map[min_hash_val]
                    topTweet_obj[4].add(row["uid"])
                    topTweet_obj[5] += row["share_count"] + 1
                    topTweet_obj[6] += row["likes_count"]
                    unique_tweets_map[min_hash_val] = topTweet_obj

                links = []
                if type(row["url"]) == str:
                    try:
                        urls = []
                        urls_raw = ast.literal_eval(row["url"])
                        for url in urls_raw:
                            urls.append(url["expanded_url"])
                    except ValueError:
                        urls = row["url"].split(",")

                    
                else:
                    new_text = row["tweet_text"].rsplit(' ', 1)[0]
                    found_urls = re.findall("https?://t\.co/\S+", new_text)

                    urls = []
                    for url_idx in range(len(found_urls)): 
                        count = len(found_urls[url_idx])-1 
                        while found_urls[url_idx][count] not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789": 
                            count -= 1
                            found_urls[url_idx] = found_urls[url_idx][:count+1]
                            if urls_map.get(found_urls[url_idx], None) is not None:
                                urls.append(urls_map[found_urls[url_idx]])

                for url in urls:
                    if unique_links_map.get(url, None) is None:
                        unique_links_map[url] = [url, set([row["uid"]]), row["share_count"]+1, row["likes_count"]]
                    else:
                        topLink_obj = unique_links_map[url]
                        topLink_obj[1].add(row["uid"])
                        topLink_obj[2] += row["share_count"] + 1
                        topLink_obj[3] += row["likes_count"]
                        unique_links_map[url] = topLink_obj


            top_tweets_list = list(unique_tweets_map.values())
            top_tweets_list.sort(key=lambda elem: (elem[6], elem[5], len(elem[4])), reverse=True)
            top_tweets_list = top_tweets_list[:10]
            for tweet_idx in range(len(top_tweets_list)):
                top_tweets_list[tweet_idx][4] = len(top_tweets_list[tweet_idx][4])

            top_links_list = list(unique_links_map.values())
            top_links_list.sort(key=lambda elem: (elem[3], elem[2], len(elem[1])), reverse=True)
            top_links_list = top_links_list[:10]
            for tweet_idx in range(len(top_links_list)):
                top_links_list[tweet_idx][1] = len(top_links_list[tweet_idx][1])


            bot_count = len(tweet_df["uid"].unique())
            tweet_number = len(tweet_df.index)
            tweet_text = list(tweet_text)

            #tweet_df["phrase_shares"] = tweet_df.apply(calc_phrase_shares, args = (phrases_shares,), axis=1)
            #tweet_df["phrase_freq"] = tweet_df.apply(calc_phrase_freq, args = (phrases_freq,), axis=1)
            #tweet_df["hashtag_shares"] = tweet_df.apply(calc_hashtags_shares, args = (hashtags_shares,), axis=1)
            #tweet_df["hashtag_freq"] = tweet_df.apply(calc_hashtags_freq, args = (hashtags_freq,), axis=1)
            #tweet_df = tweet_df.sort_values(by=['phrase_shares', 'hashtag_shares','phrase_freq', 'hashtag_freq'])
            #tweet_text_list = []
            #for idx, row in tweet_df[:10].iterrows():
            #    tweet_text = "Tweet: " + row["tweet_text"]
            #    tweet_text_list.append(tweet_text)
            #shares = sum([i[2] for i in phrases_list])
            #bot_count = sum([i[3] for i in phrases_list])
            #max_share_count = max(max_share_count, shares)
            #max_freq_count = max(max_freq_count, bot_count)
            #min_share_count = min(min_share_count, shares)
            #min_freq_count = min(min_freq_count, bot_count)
            clusters_list.append([clean_phrases,ctr, likes, shares, bot_count, tweet_number, top_tweets_list, top_links_list])
            n += 1


    #non_en_clusters_list = []
    #for idx, c in enumerate(non_en_clusters):
    #    if len(c) > 7:
    #        non_en_clusters_list.append(["Topic "+ str(idx), "\n".join(c[:10])])
    clusters_list.sort(key=lambda elem: (elem[2],elem[3], elem[4]), reverse=True)
    for c_idx in range(len(clusters_list)):
        clusters_list[c_idx] = [tool_config["date"][0], tool_config["date"][1], "Topic " + str(c_idx)] + clusters_list[c_idx]
    if len(clusters_list) > 0:
        clusters_df = pd.DataFrame(clusters_list)
        clusters_df.columns = ["Start date", "End date", "Topic Number", "Keywords", "Hashtags", "Likes Count", "Shares Count", "Bot Count", "Tweets Count", "Top Tweets", "Top Links"]
        filename = "{}_{}_{}_topic_clusters.csv".format(tool_config["week_str"], country, prefix)
        clusters_df.to_csv(tool_config["result_file_loc"].format(filename), index=False)
    #if len(non_en_clusters_list) > 0:
    #    non_en_clusters_df = pd.DataFrame(non_en_clusters_list)
    #    non_en_clusters_df.columns = ["Topic Number", "Keywords"]
    #    non_en_clusters_df.to_csv("/".join(["WeeklyData", week_str, "Results", country + "_non_en_topic_clusters.csv"]), index=False)
    return urls_set
 

def calculate_clusters(tool_config):

    filename = tool_config["week_str"] + "_all_tweets_preprocessing.pkl"
    try:
        with open(tool_config["inter_file_loc"].format(filename), "rb") as f1:
            all_country_en_dfs, all_langs_non_en_dfs = pickle.load(f1)
        print("Using tweets intermediate file")

    except FileNotFoundError:
        all_country_en_dfs, all_langs_non_en_dfs = get_preprocessed_data(tool_config)
        with open(tool_config["inter_file_loc"].format(filename), "wb") as f1:
            pickle.dump((all_country_en_dfs, all_langs_non_en_dfs), f1)

    topic_filename = tool_config["week_str"] +"_topic_preprocessing.pkl"
    
    try:
        with open(tool_config["inter_file_loc"].format(topic_filename), "rb") as f1:
            country_topic_en_preprocessed, lang_topic_non_en_preprocessed = pickle.load(f1)
        print("Using topic intermediate file")
    except FileNotFoundError:
        country_tweets = defaultdict(list)
        all_tweets = []
        country_topic_en_preprocessed = {}
        lang_topic_non_en_preprocessed = {}

        for key, df in all_country_en_dfs.items():
            preprocessing_dict = preprocessing.topic_preprocessing(df)
            if len(preprocessing_dict) > 0:
                country_topic_en_preprocessed[key] = preprocessing_dict

        for key, df in all_langs_non_en_dfs.items():
            preprocessing_dict = preprocessing.topic_preprocessing(df,en=False)
            if len(preprocessing_dict) > 0:
                lang_topic_non_en_preprocessed[key] = preprocessing_dict

        with open(tool_config["inter_file_loc"].format(topic_filename), "wb") as f1:
            pickle.dump((country_topic_en_preprocessed, lang_topic_non_en_preprocessed), f1)
    clusters = {}
    non_en_clusters = {}

    with open("./urls_map.pkl","rb") as f1:
        urls_map = pickle.load(f1)
    urls_set = set()
    try:
        with open(tool_config["inter_file_loc"].format(tool_config["week_str"] + "_clusters.pkl"), "rb") as f1:
            clusters, non_en_clusters = pickle.load(f1)
        for key, topic_dict in country_topic_en_preprocessed.items():
            urls_set = save_hashtag_clusters(
                clusters[key], 
                topic_dict, 
                all_country_en_dfs[key], True, tool_config, key, urls_map, urls_set)

        for key, topic_dict in lang_topic_non_en_preprocessed.items():
            urls_set = save_hashtag_clusters(
                non_en_clusters[key], 
                topic_dict, 
                all_langs_non_en_dfs[key], False, tool_config, key, urls_map, urls_set)
 
    except:
        for key, topic_dict in country_topic_en_preprocessed.items():
            clusters[key] = clustering.calculate_topics_by_hashtags(
                topic_dict["hashtags"],
                topic_dict["hashtags_phrases"], 
                tool_config["minPoints"], tool_config["epsilon"])
            urls_set = save_hashtag_clusters(
                clusters[key], 
                topic_dict, 
                all_country_en_dfs[key], True, tool_config, key, urls_map, urls_set)

        for key, topic_dict in lang_topic_non_en_preprocessed.items():
            non_en_clusters[key] = clustering.calculate_topics_by_hashtags(
                topic_dict["hashtags"],
                topic_dict["hashtags_phrases"], 
                tool_config["minPoints"], tool_config["epsilon"])
            urls_set = save_hashtag_clusters(
                non_en_clusters[key], 
                topic_dict, 
                all_langs_non_en_dfs[key], False, tool_config, key, urls_map, urls_set)
 
    with open(tool_config["inter_file_loc"].format(tool_config["week_str"] + "_urls_set.pkl"), "wb") as f1:
        pickle.dump(urls_set, f1)
    with open(tool_config["inter_file_loc"].format(tool_config["week_str"] + "_clusters.pkl"), "wb") as f1:
        pickle.dump((clusters, non_en_clusters), f1)



    #clusters = clustering.calculate_topics_by_hashtags(preprocessed_data["hashtags"], preprocessed_data["hashtags_phrases"], tool_config["epsilon"], tool_config["minPoints"])
    return []
