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


eu_countries = set(["czech", "denmark", "estonia", "finland", "france", "hungary", "netherlands", "norway", "sweden"])
only_en_countries = set(["uk","usa"])
all_countries = list(only_en_countries) + list(eu_countries) + ["eu"]


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
    #if type(row["tweet_stats"]) == str:
    #    vals = ast.literal_eval(row["tweet_stats"])
    #    return int(vals["reply_count"]) + int(vals["retweet_count"]) + int(vals["quote_count"])
    #else:
    return int(row["quote_count"] + row["reply_count"] + row["retweet_count"])

def calc_likes(row):
    if type(row["tweet_stats"]) == str:
        vals = ast.literal_eval(row["tweet_stats"])
        return int(vals["favorite_count"])
    else:
        return int(row["likes_count"])

def calc_shares_coronavirus(row):
    if type(row["tweet_stats"]) == str:
        vals = ast.literal_eval(row["tweet_stats"])
        return int(vals["reply_count"]) + int(vals["retweet_count"]) + int(vals["quote_count"])
    else:
        return int(row["quotes_count"] + row["reply_count"] + row["retweet_count"])

def calc_likes_coronavirus(row):
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

    if len(phrases) == 0:
        for each in ranked_phrases:
            if each[0] > 1.0:
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




def calculate_hashtags_order(hashtags_freq, en=True):

    hash_tags = sorted(hashtags_freq.items(), key=lambda item: item[1], reverse=True)
    idx = 0

    threshold = 7
    if not en:
        threshold = 3

    for ht in hash_tags:
        if ht[1] < threshold:
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
    #hashtags_str = row["hashtags"].replace("'", '"')
    #hashtags = json.loads(hashtags_str)
    hashtag_share_count = 0
    hashtags = row["hashtags"].split(",")
    for ht in hashtags:
        hash_t = ht.lower()
        hashtag_share_count += hashtags_shares[hash_t]
    return hashtag_share_count

def calc_phrase_freq(row, phrases_freq):
    phrases = row["phrases"]
    phrase_freq_sum = 0
    for ph in phrases:
        phrase_freq_sum += phrases_freq[ph]

    return phrase_freq_sum

def calc_hashtags_freq(row, hashtags_freq):
    #hashtags_str = row["hashtags"].replace("'", '"')
    #hashtags = json.loads(hashtags_str)
    hashtag_freq_count = 0
    hashtags = row["hashtags"].split(",")
    for ht in hashtags:
        hash_t = ht.lower()
        hashtag_freq_count += hashtags_freq[hash_t]
    return hashtag_freq_count


def topic_preprocessing(df, technique=True, en=True):
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
            if not (type(row["tid"]) == str or type(row["tid"]) == float or type(row["tid"]) == int):
                import pdb; pdb.set_trace()
            phrases_tweets[phrase].add(row["tid"])
            if type(row["hashtags"]) == str:
                hashtags = row["hashtags"].split(",")
                #hashtags_str = row["hashtags"].replace("'", '"')
                #try:
                    #hashtags = json.loads(hashtags_str)
                for ht in hashtags:
                    hash_t = ht.lower()
                    phrases_htgs[phrase].add(hash_t)
                    hashtags_freq[hash_t] += 1
                    hashtags_phrases[hash_t].add(phrase)
                    hashtags_tweets[hash_t].add(row["tid"])
                    hashtags_shares[hash_t] += row["share_count"]
                    hashtags_likes[hash_t] += row["likes_count"]
                #except json.JSONDecodeError:
                #    print(hashtags_str.split())
                #    for ht in hashtags_str.split():
                #        hash_t = ht.strip()
                #        phrases_htgs[phrase].add(hash_t)
                #        hashtags_freq[hash_t] += 1
                #        hashtags_phrases[hash_t].add(phrase)
                #        hashtags_tweets[hash_t].add(row["tid"])
                #        hashtags_shares[hash_t] += row["share_count"]
                #        hashtags_likes[hash_t] += row["likes_count"]
            if technique and "nhashtag" in df.columns and type(row["nhashtag"]) == set and len(row["nhashtag"]) > 0:
                for hash_t in row["nhashtag"]:
                    phrases_htgs[phrase].add(hash_t)
                    hashtags_freq[hash_t] += 1
                    hashtags_phrases[hash_t].add(phrase)
                    hashtags_tweets[hash_t].add(row["tid"])
                    hashtags_shares[hash_t] += row["share_count"]
                    hashtags_likes[hash_t] += row["likes_count"]



    phrases, phrases_tf_ihf = calculate_phrase_tf_ihf(phrases_freq, phrases_htgs) 
    hashtags = calculate_hashtags_order(hashtags_freq, en)


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

def find_word_in_str(strg, ph, flag=False):
    punctuations = [".","!","?",","," ","'",'"']
    if flag:
        punctuations.append("'s")
    ph_list = []

    ph2 = ph.replace(" ","")
    ph3 = ph.replace(" ","-")
    ph_pos = strg.find(ph)
    ph_pos2 = strg.find(ph.replace(" ",""))
    ph_pos3 = strg.find(ph.replace(" ","-"))
    if ph_pos != -1:
        for ch in punctuations:
            for ch2 in punctuations:
                ph_list.append(ch2+ph+ch)

    if flag and ph_pos2 != -1  and " " in ph:
        new_ph = ph.replace(" ", "")
        for ch in punctuations:
            for ch2 in punctuations:
                ph_list.append(ch2+new_ph+ch)

    if flag and ph_pos3 != -1  and " " in ph:
        new_ph = ph.replace(" ", "-")
        for ch in punctuations:
            for ch2 in punctuations:
                ph_list.append(ch2+new_ph+ch)



    for ph_strg in ph_list:
        if ph_strg in strg or \
           ph_pos == 0 or \
           ph_pos+len(ph) >= len(strg)-1 or \
           ph_pos2 == 0 or \
           ph_pos2+len(ph2) >= len(strg)-1:
            return True
    return False


def filter_tweets_coronavirus(orig_tweet_text, nphrases_dict, country):
    orig_text = orig_tweet_text.strip().lower()
    orig_text = re.sub("&amp;|&gt;|&lt;"," ", orig_text)
    orig_text = orig_text.replace("\n", " ").replace("#","").replace("@", "").lower().strip()
    orig_text = demoji.replace(orig_text," ")
    for ph,ph_country in nphrases_dict.items():
        orig_ph_pos = orig_text.find(ph)
        if country == ph_country or ph_country == "na":
            if  find_word_in_str(orig_text, ph, True):
                return True
    return False





def assign_country_tweets(orig_tweet_text, tweet_text, nphrases, phrases_country, phrases_country_freq, phrases_hashtag, eu_countries, coded_countries):
    hashtags =  set()
    countries = defaultdict(int)
    text = tweet_text.lower().strip()
    final_country = set()

    orig_tweet_text = re.sub("&amp;|&gt;|&lt;"," ", orig_tweet_text)
    orig_text = orig_tweet_text.replace("\n", " ").replace("#","").replace("@", "").lower().strip()
    orig_text = demoji.replace(orig_text," ")
    for ph in nphrases:
        ph_pos = text.find(ph)
        orig_ph_pos = orig_text.find(ph)
        if  find_word_in_str(text, ph) or find_word_in_str(orig_text, ph, True):
            if phrases_hashtag.get(ph, None) is not None: 
                hashtags.add(phrases_hashtag[ph])

            #if phrases_country.get(ph, None) is not None:
            #    if phrases_country[ph] == "eu" or phrases_country[ph] not in only_en_countries:
            #            countries["eu"] += phrases_country_freq[ph]
            #    else:
            #        countries[phrases_country[ph]] += phrases_country_freq[ph]

    #for ph, ctry in coded_countries.items():
    #    ph_pos = text.find(ph)
    #    orig_ph_pos = orig_text.find(ph)
    #    if  find_word_in_str(text, ph) or find_word_in_str(orig_text, ph, True):
    #        final_country.add(ctry)

    if len(hashtags) == 0:
        hashtags = None
    #if len(countries) == 0 and len(final_country) == 0:
    #    final_country = "eu"
    #else:
    #    if len(final_country) > 0:
    #        if "usa" in final_country:
    #            final_country = "usa"
    #        elif "uk" in final_country:
    #            final_country = "uk"
    #        else:
    #            final_country = "eu"
    #    else:

    #        country_freq_max = 0

    #        if countries.get("usa", None) is not None:
    #            final_country = "usa"
    #        elif countries.get("uk", None) is not None:
    #            final_country = "uk"
    #        else:
    #            final_country = "eu"
    #return [final_country, hashtags]
    return hashtags

def valid_phrases(row):
    return True if len(row["phrases"]) > 0 else False

def tweets_cleaning(data_df, nphrases, phrases_country, phrases_country_freq, 
                    phrases_hashtag, eu_countries, coded_countries, nmatching=True):

    #try:
    #    data_df["tweet_check"] = data_df.progress_apply(valid_tweets, axis=1)
    #except ValueError:
    #    import pdb; pdb.set_trace()

    data_df = data_df[~data_df["likes_count"].isna()]
    #data_df = data_df[data_df["tweet_check"]]
    #data_df["share_count"] = data_df.apply(calc_shares, axis=1)
    #data_df["likes_count"] = data_df.apply(calc_likes, axis=1)
    data_df["cleaned_text"] = data_df.progress_apply(beautify_tweet, axis=1)
    data_df["phrases"] = data_df.progress_apply(calc_phrases, axis=1)
    data_df["tweet_check2"] = data_df.progress_apply(valid_phrases, axis=1)
    data_df = data_df[data_df["tweet_check2"]]
    if nmatching:
        data_df["nhashtag"] = data_df.progress_apply(lambda row: assign_country_tweets(row["tweet_text"], row["cleaned_text"], nphrases, phrases_country, phrases_country_freq, phrases_hashtag, eu_countries, coded_countries), axis=1)
        data_df_htgs = data_df.progress_apply(lambda row: hashtag_type(row["hashtags"], row["nhashtag"]), axis=1)
    else:
        data_df_htgs = data_df.progress_apply(lambda row: hashtag_type(row["hashtags"], None), axis=1)
    data_df = data_df[data_df_htgs]

    data_df["share_count"] = data_df[["quotes_count", "reply_count", "retweet_count"]].sum(axis=1)

    return data_df[data_df_htgs]


def tweets_cleaning_coronavirus(data_df, nphrases, phrases_country, phrases_country_freq, 
                                phrases_hashtag, eu_countries, coded_countries, nmatching=True):

    try:
        data_df["tweet_check"] = data_df.progress_apply(valid_tweets, axis=1)
    except ValueError:
        import pdb; pdb.set_trace()
    data_df = data_df[data_df["tweet_check"]]
    data_df["share_count"] = data_df.apply(calc_shares, axis=1)
    data_df["likes_count"] = data_df.apply(calc_likes, axis=1)
    data_df["cleaned_text"] = data_df.progress_apply(beautify_tweet, axis=1)
    #data_df["phrases"] = data_df.progress_apply(calc_phrases, axis=1)
    #data_df["tweet_check2"] = data_df.progress_apply(valid_phrases, axis=1)
    #data_df = data_df[data_df["tweet_check2"]]
    data_df["nhashtag"] = data_df.apply(lambda row: assign_country_tweets(row["tweet_text"], row["cleaned_text"], nphrases, phrases_country, phrases_country_freq, phrases_hashtag, eu_countries, coded_countries), axis=1)
    #    data_df_htgs = data_df.progress_apply(lambda row: hashtag_type(row["hashtags"], row["nhashtag"]), axis=1)
    #else:
    #    data_df_htgs = data_df.progress_apply(lambda row: hashtag_type(row["hashtags"], none), axis=1)


    return data_df




def cluster_phrases(cluster, hashtag_phrases_map):
    result = set()
    cluster_set = set(cluster)
    for ht in cluster_set:
        result = result.union(hashtag_phrases_map[ht])

    return result

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
 
