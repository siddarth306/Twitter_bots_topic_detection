import pickle
import pandas as pd
from collections import defaultdict
from utils import preprocessing
from utils import clustering
import numpy as np
import ast

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
only_en_countries = ["uk","usa"]
all_countries = only_en_countries + list(eu_countries)

def hashtag_filter(hashtag):
    return True if type(hashtag) == str else False


def get_preprocessed_data(tool_config):
    data_df = pd.DataFrame()
    all_country_dfs = {}
    all_country_non_en_dfs = {}

    phrases_country = {}
    phrases_hashtag = {}
    nphrases = []
    country_filename = "country-coded-nouns.csv"
    country_phrases_df = pd.read_csv(tool_config["input_out_file_loc"].format(country_filename))

    for idx, row in country_phrases_df.iterrows():
        nphrases.append(row["Phrase"])
        if type(row["Country"]) == str and len(row["Country"]) > 0:
            phrases_country[row["Phrase"]] = row["Country"]
        if type(row["#hashtag"]) == str and len(row["#hashtag"]) > 0:
            phrases_hashtag[row["Phrase"]] = row["#hashtag"]

    #nphrases.sort(key= lambda x: x[1], reverse=True)

    import pdb; pdb.set_trace()
    print("Preprocessing tweets")
    for file_n in [*country_map.keys()]:
        print("Processing " + file_n)
        country_df = pd.read_csv(tool_config["input_file_loc"].format( file_n))
        if country_map2[file_n] not in only_en_countries:
            country_non_en_df = country_df[country_df["language"] != "en"]
            country_non_en_df = preprocessing.tweets_cleaning(country_non_en_df, nphrases, phrases_country, phrases_hashtag, eu_countries, False)
            all_country_non_en_dfs[country_map2[file_n]] = country_non_en_df
        country_df = country_df[country_df["language"]=="en"]
        country_df = preprocessing.tweets_cleaning(country_df, nphrases, phrases_country, phrases_hashtag, eu_countries)
        data_df = data_df.append(country_df, ignore_index = True)
        country_df = country_df[country_df.apply(lambda row: hashtag_filter(row["hashtags"]), axis=1)]
        all_country_dfs[country_map2[file_n]] = country_df

    #preprocessed_data = preprocessing.topic_preprocessing(data_df)

    return data_df, all_country_dfs, all_country_non_en_dfs

def remove_wrong_country_tweets(tid, country_tids, all_tids):
    if tid not in country_tids and tid in all_tids:
        return False
    return True

def save_hashtag_clusters(clusters, topic_preprocessed, data_df, en, tool_config, country):
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
    for idx, c in enumerate(clusters):
        phrases = set()
        tweet_tids = set()
        for ht in c:
            for ph in hashtags_phrases[ht]:
                if phrase_tf_ihf.get(ph, None) is None:
                    tf_score = -1
                else:
                    tf_score = phrase_tf_ihf[ph]
                share_count = phrases_shares[ph]
                freq_count = phrases_freq[ph]
                phrases.add((ph,tf_score, phrases_shares[ph], phrases_freq[ph]))
        if len(phrases) > 7:

            phrases_list = list(phrases)
            phrases_list.sort(key=lambda x: (x[1], x[2], x[3]), reverse= True)
            clean_phrases = [i[0] for i in phrases_list[:10]]
            for ph in phrases_list:
                tweet_tids.union(phrases_tweets[ph])
            
            tweet_df = data_df[data_df['tid'].isin(list(tweet_tids))]
            shares = tweet_df["share_count"].sum()
            likes = tweet_df["likes_count"].sum()
            bot_set = set()
            tweet_df.sort_values(by=['likes_count', 'share_count'])
            tweet_text = []
            links = []
            for idx, row in tweet_df.iterrows():
                if len(tweet_text) < 10:
                    tweet_text.append(row["tweet_text"])
                if len(links) < 10:
                    try:
                        urls = ast.literal_eval(row["url"])
                        for url in urls:
                            if len(links) <= 10:
                                links.append(url["expanded_url"])
                    except ValueError:
                        urls = row["urls"].split(",")
                        links = links + urls


                if not np.isnan(row["uid"]):
                    bot_set.add(int(row["uid"]))
                elif not np.isnan(row["user_id"]):
                    bot_set.add(int(row["user_id"]))
            links = links[:10]

            bot_count = len(bot_set)
            tweet_number = tweet_df.count


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
            clusters_list.append(["Topic " + str(n), "\n".join(clean_phrases),"\n".join(c[:10]), likes, shares, bot_count, tweet_number, tweet_text, links])
            n += 1


    #non_en_clusters_list = []
    #for idx, c in enumerate(non_en_clusters):
    #    if len(c) > 7:
    #        non_en_clusters_list.append(["Topic "+ str(idx), "\n".join(c[:10])])

    if len(clusters_list) > 0:
        clusters_df = pd.DataFrame(clusters_list)
        clusters_df.columns = ["Topic Number", "Keywords", "Hashtags", "Likes Count", "Shares Count", "Bot Count", "Tweets Count", "Top Tweets", "Top Links"]
        filename = "{}_{}_{}_topic_clusters.csv".format(tool_config["week_str"], country, prefix)
        clusters_df.to_csv(tool_config["result_file_loc"].format(filename), index=False)
    
    #if len(non_en_clusters_list) > 0:
    #    non_en_clusters_df = pd.DataFrame(non_en_clusters_list)
    #    non_en_clusters_df.columns = ["Topic Number", "Keywords"]
    #    non_en_clusters_df.to_csv("/".join(["WeeklyData", week_str, "Results", country + "_non_en_topic_clusters.csv"]), index=False)
 

def calculate_clusters(tool_config):

    filename = tool_config["week_str"] + "_all_en_topic_preprocessing.pkl"
    try:
        with open(tool_config["inter_file_loc"].format(filename), "rb") as f1:
            data_df, all_country_dfs, all_country_non_en_dfs = pickle.load(f1)
        print("Using tweets intermediate file")

    except FileNotFoundError:
        data_df, all_country_dfs, all_country_non_en_dfs = get_preprocessed_data(tool_config)
        with open(tool_config["inter_file_loc"].format(filename), "wb") as f1:
            pickle.dump((data_df, all_country_dfs, all_country_non_en_dfs), f1)

    topic_filename = tool_config["week_str"] +"_topic_preprocessing.pkl"
    try:
        with open(tool_config["inter_file_loc"].format(topic_filename), "rb") as f1:
            country_topic_preprocessed, country_non_en_topic_preprocessed, country_dfs_processed, all_country_non_en_dfs = pickle.load(f1)
        print("Using topic intermediate file")
    except FileNotFoundError:
        country_tweets = defaultdict(list)
        all_tweets = []

        for idx, row in data_df.iterrows():
            if row["ncountry"] is not None:
                for ct in row["ncountry"]:
                    country_tweets[ct].append(row["tid"])
                    all_tweets.append(row["tid"])

        country_topic_preprocessed = {}
        country_non_en_topic_preprocessed = {}

        country_dfs_processed = {}
        usa_df = data_df.loc[data_df["tid"].isin(country_tweets["usa"])]
        country_dfs_processed["usa"] = usa_df
        country_topic_preprocessed["usa"] = preprocessing.topic_preprocessing(usa_df)
        all_tweets = set(all_tweets)
        import pdb; pdb.set_trace()
        for file_n in [*country_map.keys()]:
            additional_tids = country_tweets[country_map2[file_n]]
            additional_tweets = data_df.loc[data_df["tid"].isin(additional_tids)]
            c_df = all_country_dfs[country_map2[file_n]]
            combined_c_df = pd.concat([c_df,additional_tweets])
            combined_c_df.drop_duplicates(subset="tid", inplace=True, keep="last")
            ct_tweets_set = set(country_tweets[country_map2[file_n]])
            combined_c_df["valid_tweets"] = combined_c_df.apply(lambda row: remove_wrong_country_tweets(row["tid"], ct_tweets_set, all_tweets), axis=1)
            new_c_df = combined_c_df[combined_c_df["valid_tweets"]]
            country_dfs_processed[country_map2[file_n]] = new_c_df
            preprocess_dict = preprocessing.topic_preprocessing(new_c_df)
            if len(preprocess_dict["phrases"]) != 0:   
                country_topic_preprocessed[country_map2[file_n]] = preprocess_dict
            if country_map2[file_n] not in only_en_countries:
                
                preprocess_dict = preprocessing.topic_preprocessing(all_country_non_en_dfs[country_map2[file_n]])
                if len(preprocess_dict["phrases"]) != 0:   
                    country_non_en_topic_preprocessed[country_map2[file_n]] = preprocess_dict
        with open(tool_config["inter_file_loc"].format(topic_filename), "wb") as f1:
            pickle.dump((country_topic_preprocessed, country_non_en_topic_preprocessed, country_dfs_processed, all_country_non_en_dfs), f1)

    clusters = {}
    non_en_clusters = {}
    clusters["usa"] = clustering.calculate_topics_by_hashtags(country_topic_preprocessed["usa"]["hashtags"],
                                                              country_topic_preprocessed["usa"]["hashtags_phrases"], 
                                                              tool_config["minPoints"], tool_config["epsilon"])
    save_hashtag_clusters(clusters["usa"], country_topic_preprocessed["usa"], country_dfs_processed["usa"], True, tool_config, "usa")
    for file_n in [*country_map.keys()]:

        if country_map2[file_n] not in only_en_countries and country_non_en_topic_preprocessed.get(country_map2[file_n], None) is not None:
            non_en_clusters[country_map2[file_n]] = clustering.calculate_topics_by_hashtags(country_non_en_topic_preprocessed[country_map2[file_n]]["hashtags"],
                                                                                 country_non_en_topic_preprocessed[country_map2[file_n]]["hashtags_phrases"],
                                                                                 tool_config["minPoints"], tool_config["epsilon"])
            save_hashtag_clusters(non_en_clusters[country_map2[file_n]], country_non_en_topic_preprocessed[country_map2[file_n]], all_country_non_en_dfs[country_map2[file_n]], False, tool_config, country_map2[file_n])
        if country_topic_preprocessed.get(country_map2[file_n], None) is not None:
            clusters[country_map2[file_n]] = clustering.calculate_topics_by_hashtags(country_topic_preprocessed[country_map2[file_n]]["hashtags"],
                                                                                     country_topic_preprocessed[country_map2[file_n]]["hashtags_phrases"],
                                                                                     tool_config["minPoints"], tool_config["epsilon"])
            save_hashtag_clusters(clusters[country_map2[file_n]], country_topic_preprocessed[country_map2[file_n]], country_dfs_processed[country_map2[file_n]], True, tool_config, country_map2[file_n])

    import pdb; pdb.set_trace()

    with open(tool_config["inter_file_loc"].format(tool_config["week_str"] + "_clusters.pkl"), "wb") as f1:
        pickle.dump(clusters, f1)



    #clusters = clustering.calculate_topics_by_hashtags(preprocessed_data["hashtags"], preprocessed_data["hashtags_phrases"], tool_config["epsilon"], tool_config["minPoints"])

    return []
