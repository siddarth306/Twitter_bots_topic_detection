import pandas as pd
import re
import ast
import numpy as np
import sys
from rake_nltk import Rake
import demoji
import json
from tqdm import tqdm
from tqdm._tqdm_notebook import tqdm_notebook
import pickle
tqdm_notebook.pandas()
from collections import defaultdict
demoji.download_codes()

cs_rake = Rake(language="czech")
da_rake = Rake(language="danish")
et_rake = Rake(language="estonian")
fi_rake = Rake(language="finnish")
fr_rake = Rake(language="french")
hu_rake = Rake(language="hungarian")
nl_rake = Rake(language="dutch")
no_rake = Rake(language="norwegian")
sv_rake = Rake(language="swedish")
en_rake = Rake(language="english")

rake_mapper = {
    "cs": cs_rake,
    "da": da_rake,
    "et": et_rake,
    "fi": fi_rake,
    "fr": fr_rake,
    "hu": hu_rake,
    "nl": nl_rake,
    "no": no_rake,
    "sv": sv_rake,
    "en": en_rake,
}


def beautify_tweet(row):
    tweet_text = demoji.replace(row["tweet_text"],"")
    tweet_text = re.sub(r"(?:\@|https?\://)\S+", "", tweet_text)
    tweet_text = re.sub(r"#(\w+)","",tweet_text)
    tweet_text = re.sub("RT|,|[\W\d!@#$%&*:\/]*…|\*|&amp;|&gt;|&lt;",
           "", tweet_text)
    tweet_text = re.sub("’|‘|”|“", "", tweet_text)
    tweet_text = re.sub("[-«\[\]\(\)\<\>\{\}»—\\\@\#\$\%\&\:\/]|[\.]+|[\!]+|[\?]+|\n", "", tweet_text)
    return tweet_text

def valid_tweets(row):
    return True if type(row["tweet_stats"]) == str or type(row["likes_count"]) == np.float64 else False

def calc_shares(row):
    if type(row["tweet_stats"]) == str:
        vals = ast.literal_eval(row["tweet_stats"])
        return int(vals["reply_count"]) + int(vals["retweet_count"]) + int(vals["quote_count"])
    else:
        return int(row["quote_count"] + row["reply_count"] + row["retweet_count"])

def calc_likes(row):
    if type(row["tweet_stats"]) == str:
        vals = ast.literal_eval(row["tweet_stats"])
        return int(vals["favorite_count"])
    else:
        return int(row["likes_count"])




def calc_phrases(row):
    phrases = set()
    r = rake_mapper[row["language"]]
    r.extract_keywords_from_text(row["cleaned_text"])
    ranked_phrases = r.get_ranked_phrases_with_scores()
    for each in ranked_phrases:
        if each[0] > 3.0:
            phrases.add(each[1])

    return phrases

def hashtag_type(hashtags, nhashtags):
    return True if type(hashtags) == str or (type(nhashtags) == set and len(nhashtags) > 0)  else False


def calculate_phrase_tf_ihf(phrase_freq, phrase_htgs):
    phrases = []
    phrases_tf_ihf= {}
    for key, val in phrase_freq.items():
        try:
            tf_ihf = val / len(phrase_htgs[key])
        except ZeroDivisionError:
            import pdb; pdb.set_trace()
        if tf_ihf > 1.0:
            phrases.append([key, tf_ihf])
            phrases_tf_ihf[key] = tf_ihf

    phrases.sort(key=lambda x: x[1], reverse=True)
    if len(phrases) > 0:
        print(phrases[0], phrases[-1])
    return phrases, phrases_tf_ihf




def calculate_hashtags_order(hashtags_freq):

    hash_tags = sorted(hashtags_freq.items(), key=lambda item: item[1], reverse=True)
    idx = 0
    for ht in hash_tags:
        if ht[1] < 7:
            break
        idx += 1
    print(hash_tags[0], hash_tags[-1])
    return hash_tags[:idx+1]


def calc_phrase_shares(row, phrases_shares):
    phrases = row["phrases"]
    phrase_shares_sum = 0
    for ph in phrases:
        phrase_shares_sum += phrases_shares[ph]

    return phrase_shares_sum

def calc_hashtags_shares(row, hashtags_shares):
    hashtags_str = row["hashtags"].replace("'", '"')
    hashtags = json.loads(hashtags_str)
    hashtag_share_count = 0
    for ht in hashtags:
        hash_t = ht["text"].lower()
        hashtag_share_count += hashtags_shares[hash_t]
    return hashtag_share_count

def calc_phrase_freq(row, phrases_freq):
    phrases = row["phrases"]
    phrase_freq_sum = 0
    for ph in phrases:
        phrase_freq_sum += phrases_freq[ph]

    return phrase_freq_sum

def calc_hashtags_freq(row, hashtags_freq):
    hashtags_str = row["hashtags"].replace("'", '"')
    hashtags = json.loads(hashtags_str)
    hashtag_freq_count = 0
    for ht in hashtags:
        hash_t = ht["text"].lower()
        hashtag_freq_count += hashtags_freq[hash_t]
    return hashtag_freq_count


def topic_preprocessing(df):
    phrases_freq = defaultdict(int)
    phrases_htgs = defaultdict(set)
    phrases_shares = defaultdict(int)
    phrases_likes = defaultdict(int)
    phrases_tweets = defaultdict(set)
    hashtags_tweets = defaultdict(set)
    hashtags_freq = defaultdict(int)
    hashtags_phrases = defaultdict(set)
    hashtags_shares = defaultdict(int)
    hashtags_likes = defaultdict(int)
    phrases_map = {}
    print("Finding phrases")
    for index, row in df.iterrows():
        for phrase in row["phrases"]:
            phrases_freq[phrase] += 1
            phrases_shares[phrase] += row["share_count"]
            phrases_likes[phrase] += row["likes_count"]
            phrases_tweets[phrase].add(row["tid"])
            if type(row["hashtags"]) == str:
                hashtags_str = row["hashtags"].replace("'", '"')
                try:
                    hashtags = json.loads(hashtags_str)
                    for ht in hashtags:
                        hash_t = ht["text"]
                        phrases_htgs[phrase].add(hash_t)
                        hashtags_freq[hash_t] += 1
                        hashtags_phrases[hash_t].add(phrase)
                        hashtags_tweets[hash_t].add(row["tid"])
                        hashtags_shares[hash_t] += row["share_count"]
                        hashtags_likes[hash_t] += row["likes_count"]
                except json.JSONDecodeError:
                    for ht in hashtags.split():
                        hasht_t = ht.strip()
                        phrases_htgs[phrase].add(hash_t)
                        hashtags_freq[hash_t] += 1
                        hashtags_phrases[hash_t].add(phrase)
                        hashtags_tweets[hash_t].add(row["tid"])
                        hashtags_shares[hash_t] += row["share_count"]
                        hashtags_likes[hash_t] += row["likes_count"]
            if "nhashtag" in df.columns and type(row["nhashtag"]) == set and len(row["nhashtag"]) > 0:
                for hash_t in row["nhashtag"]:
                    phrases_htgs[phrase].add(hash_t)
                    hashtags_freq[hash_t] += 1
                    hashtags_phrases[hash_t].add(phrase)
                    hashtags_tweets[hash_t].add(row["tid"])
                    hashtags_shares[hash_t] += row["share_count"]
                    hashtags_likes[hash_t] += row["likes_count"]



    phrases, phrases_tf_ihf = calculate_phrase_tf_ihf(phrases_freq, phrases_htgs) 
    hashtags = calculate_hashtags_order(hashtags_freq)


    preprocessed_data = {
        "phrases": phrases,
        "phrases_freq": phrases_freq,
        "phrases_htgs": phrases_htgs,
        "phrases_shares": phrases_shares,
        "phrases_tweets": phrases_tweets,
        "phrases_tf_ihf": phrases_tf_ihf,
        "hashtags": hashtags,
        "hashtags_freq": hashtags_freq,
        "hashtags_phrases": hashtags_phrases,
        "hashtags_shares": hashtags_shares,
        "hashtags_tweets": hashtags_tweets
    }
    return preprocessed_data

def assign_country_tweets(tweet_text, nphrases, phrases_country, phrases_hashtag, eu_countries):
    hashtags =  set()
    countries = set()
    text = tweet_text.lower().strip()
    for ph in nphrases:
        ph_pos = text.find(ph)
        if  ph_pos != -1 and (" "+ph+" " in text or ph_pos == 0 or ph_pos+len(ph) == len(text) ):
            if phrases_hashtag.get(ph, None) is not None: 
                hashtags.add(phrases_hashtag[ph])
            if phrases_country.get(ph, None) is not None:
                if phrases_country[ph] == "eu":
                    countries.update(eu_countries)
                else:
                    countries.add(phrases_country[ph])

    if len(hashtags) == 0:
        hashtags = None
    if len(countries) == 0:
        countries = None
    return [countries, hashtags]



def tweets_cleaning(data_df, nphrases, phrases_country, phrases_hashtag, eu_countries, nmatching=True):

    data_df["tweet_check"] = data_df.progress_apply(valid_tweets, axis=1)
    data_df = data_df[data_df["tweet_check"]]
    data_df["share_count"] = data_df.apply(calc_shares, axis=1)
    data_df["likes_count"] = data_df.apply(calc_likes, axis=1)
    data_df["cleaned_text"] = data_df.progress_apply(beautify_tweet, axis=1)
    data_df["phrases"] = data_df.progress_apply(calc_phrases, axis=1)
    if nmatching:
        data_df[["ncountry","nhashtag"]] = data_df.apply(lambda row: pd.Series(assign_country_tweets(row["cleaned_text"], nphrases, phrases_country, phrases_hashtag, eu_countries)), axis=1)
        data_df_htgs = data_df.progress_apply(lambda row: hashtag_type(row["hashtags"], row["nhashtag"]), axis=1)
    else:
        data_df_htgs = data_df.progress_apply(lambda row: hashtag_type(row["hashtags"], None), axis=1)


    return data_df[data_df_htgs]
 

#def tweet_preprocessing(data_df):
#    args = sys.argv
#    week = sys.argv[1]
#    lang_file = "all"
#    country = lang_file.replace(".csv","")
#    lang = "all"
#    week_str = "week" + week
#
#    try:
#        with open("/".join(["WeeklyData", week_str, lang + "_en_topics_preprocessing.pkl"]), "rb") as f1:
#            en_phrases, en_phrases_freq, en_phrases_htgs, en_phrases_shares, en_phrases_tweets, en_phrases_tf_ihf, en_hashtags, en_hashtags_freq, en_hashtags_phrases, en_hashtags_shares, en_hashtags_tweets, en_data_df = pickle.load(f1)
#    except FileNotFoundError:
#
#        data_df = pd.DataFrame()
#        for fl in country_map.keys():
#            ctry_data_df = pd.read_csv("/".join(["WeeklyData", week_str, fl]))
#            ctry_data_df["tweet_check"] = ctry_data_df.progress_apply(valid_tweets, axis=1)
#            ctry_data_df = ctry_data_df[ctry_data_df["tweet_check"]]
#            ctry_data_df = ctry_data_df[ctry_data_df["language"]=="en"]
#            ctry_data_df["shares"] = ctry_data_df.apply(calc_shares, axis=1)
#            ctry_data_df["tweet_text"] = ctry_data_df.progress_apply(beautify_tweet, axis=1)
#            ctry_data_df["phrases"] = ctry_data_df.progress_apply(calc_phrases, axis=1)
#            data_df = data_df.append(ctry_data_df)
#
#        data_htgs_df = data_df.progress_apply(hashtag_type, axis=1)
#
#        data_df = data_df[data_htgs_df]
#        print("Cleaned_tweets_successfully")
#        en_data_df = data_df
#
#        #non_en_data_df = data_df[data_df['language']!="en"]
#        print("Pre-processing en data")
#        
#        preprocessed_data= topic_preprocessing(en_data_df, True, week_str, lang)
#
#        return preprocessed_data
 
