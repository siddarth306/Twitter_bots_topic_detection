import pandas as pd
import sys
import ast
import json


en_files = ["usa","uk","eu"]
non_en_files = ["cs", "da", "fi","fr","et", "nl","no","sv"]
args = sys.argv
week = args[1]
week_str = "week" + week
weeks = [1,2,3,4,5,6,7,8,9,10]
run_weeks = weeks[1:]

folder_location1 = "/home/sid/CIPS/Results_merged_old/{}_clusters/".format(week_str)
folder_location3 = "/home/sid/CIPS/Results_merged/{}_clusters/".format(week_str)
folder_location3_json = "/home/sid/CIPS/Results_merged/JSONs/"
folder_location2 = "ResultData/{}/".format(week_str)

def sort_hashtags(hashtags):
    hashtags = ast.literal_eval(hashtags)
    hashtags.sort()
    return str(hashtags)


def default_handler(obj):
    for key in ['Keywords', 'Hashtags']:
        obj[key] = ast.literal_eval(obj[key])

    # 'set' is not JSON serializable
    history = ast.literal_eval(obj['Topic_History'])
    topic_history = dict()
    for week, idx in history.items():
        topic_history[week] = list(idx)
    obj['Topic_History'] = topic_history

    # modify top tweets
    tweets = ast.literal_eval(obj['Top Tweets'])
    top_tweets = []
    for tweet in tweets:
        tdict = dict({"tweet_text": tweet[1],
                      "tid": tweet[2],
                      "total_likes": "",
                      "total_shares": "",
                      "bot_counts": ""})
        top_tweets.append(tdict)
    obj['Top Tweets'] = top_tweets

    # modify top links
    links = ast.literal_eval(obj['Top Links'])
    top_links = []
    for link in links:
        ldict = dict({"link": link,
                      "total_likes": "",
                      "total_shares": "",
                      "bot_counts": ""})
        top_links.append(ldict)
    obj['Top Links'] = top_links

    return obj

#for country in en_files:
#    filename1 = folder_location1 + "{}_{}_en_topic_clusters.csv".format(week_str,country)
#    filename2 = folder_location2 + "{}_{}_en_topic_clusters.csv".format(week_str,country)
#    filename3 = folder_location3 + "{}_{}_en_topic_clusters.csv".format(week_str,country)
#    df1 = pd.read_csv(filename1)
#    df2 = pd.read_csv(filename2)
#    df1["sorted_hashtags"] = df1.apply(lambda row: sort_hashtags(row["Hashtags"]), axis=1)
#    df2["sorted_hashtags"] = df2.apply(lambda row: sort_hashtags(row["Hashtags"]), axis=1)
#    print(df1.columns)
#    if "Topic_History" in df1.columns:
#        df1 = df1[["Topic Number", "Keywords", "Hashtags", "sorted_hashtags", "Topic_History"]]
#    else:
#        df1 = df1[["Topic Number", "Keywords", "Hashtags", "sorted_hashtags"]]
#
#    df2 = df2[["sorted_hashtags", "Start date", "End date", "Likes Count", "Shares Count", "Bot Count", "Tweets Count", "Top Tweets", "Top Links"]]
#    df3 = df1.merge(df2, on='sorted_hashtags', how='left')
#    df3 = df3.drop(columns=['sorted_hashtags'])
#
#    if "Topic_History" in df1.columns:
#        columns = ["Start date", "End date", "Topic Number", "Keywords", "Hashtags", "Likes Count", "Shares Count", "Bot Count",
#                   "Tweets Count", "Top Tweets", "Top Links", "Topic_History"]
#    else:
#        columns = ["Start date", "End date", "Topic Number", "Keywords", "Hashtags", "Likes Count", "Shares Count", "Bot Count",
#                   "Tweets Count", "Top Tweets", "Top Links"]
#
#    df3 = df3[columns]
#    df3 = df3.sort_values(by=['Likes Count', 'Shares Count', "Bot Count"], ascending=False)
#    df3.to_csv(filename3, index=False)


for country in en_files:
    filename1 = folder_location1 + "{}_{}_en_topic_clusters.csv".format(week_str,country)
    filename2 = folder_location2 + "{}_{}_en_topic_clusters.csv".format(week_str,country)
    filename3 = folder_location3 + "{}_{}_en_topic_clusters.csv".format(week_str,country)
    df1 = pd.read_csv(filename1)
    df2 = pd.read_csv(filename2)
    if len(df1.index) == 0:
        df3 = pd.DataFrame(columns = ["Start date", "End date", "Topic Number", "Keywords", "Hashtags", "Likes Count", "Shares Count", "Bot Count",
                   "Tweets Count", "Top Tweets", "Top Links", "Topic_History", "Topic_Type"])
    else:
        df1["sorted_hashtags"] = df1.apply(lambda row: sort_hashtags(row["Hashtags"]), axis=1)
        df2["sorted_hashtags"] = df2.apply(lambda row: sort_hashtags(row["Hashtags"]), axis=1)
        print(df1.columns)
        if "Topic_History" in df1.columns:
            df1 = df1[["Start date", "End date","Topic Number", "Keywords", "Hashtags", "sorted_hashtags",  "Likes Count", "Shares Count", "Bot Count", "Tweets Count", "Top Tweets", "Topic_History"]]
        else:
            df1 = df1[["Start date", "End date","Topic Number", "Keywords", "Hashtags", "sorted_hashtags",  "Likes Count", "Shares Count", "Bot Count", "Tweets Count", "Top Tweets"]]

        df2 = df2[["sorted_hashtags", "Top Links"]]
        df3 = df1.merge(df2, on='sorted_hashtags', how='left')
        df3 = df3.drop(columns=['sorted_hashtags'])

        if "Topic_History" in df1.columns:
            columns = ["Start date", "End date", "Topic Number", "Keywords", "Hashtags", "Likes Count", "Shares Count", "Bot Count",
                       "Tweets Count", "Top Tweets", "Top Links", "Topic_History"]
        else:
            columns = ["Start date", "End date", "Topic Number", "Keywords", "Hashtags", "Likes Count", "Shares Count", "Bot Count",
                       "Tweets Count", "Top Tweets", "Top Links"]

        df3 = df3[columns]
        df3 = df3.sort_values(by=['Likes Count', 'Shares Count', "Bot Count"], ascending=False)
    df3.to_csv(filename3, index=False)

