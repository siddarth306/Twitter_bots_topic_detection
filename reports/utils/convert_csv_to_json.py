import json
import ast
import pandas as pd
import sys
import re
import shutil
import os

en_files = ["usa","uk","eu"]
non_en_files = ["cs", "da", "fi","fr","et", "nl","no","sv"]
language_to_file_map = {
    "usa": ["usa"],
    "uk": ["uk"],
    "eu": ["czech", "denmark","finland","france","estonia","netherlands","norway","Sweden", "hungary"],
    "cs": ["czech"],
    "da": ["denmark"],
    "fi": ["finland"],
    "fr": ["france"],
    "et": ["estonia"],
    "nl": ["netherlands"],
    "no": ["norway"],
    "sv": ["Sweden"],
    "hu": ["hungary"],
    "usa": ["usa"],
  
}
args = sys.argv
week = args[1]
week_str = "week" + week
weeks = [8,9,10]
run_weeks = weeks

folder_location3 = "../Results_merged/{}_clusters/".format(week_str)
#folder_location3_json = "/home/sid/CIPS/Results_merged/{}_clusters/"
#folder_location2 = "ResultData/{}/".format(week_str)


def calc_Topic_Type(Topic_History):
    Topic_History_dict = ast.literal_eval(Topic_History)
    if len(Topic_History_dict) == 0:
        return "Breaking Topic"
    else:
        return "Enduring Topic"

def default_handler(obj):
    for key in ['Keywords', 'Hashtags']:
        obj[key] = ast.literal_eval(obj[key])

    # 'set' is not JSON serializable
    history = ast.literal_eval(obj['Topic_History'])
    Topic_History = dict()
    if len(history) > 0:
        for week, idx in history.items():
            Topic_History[week] = list(idx)
    obj['Topic_History'] = Topic_History

    # modify top tweets

    tweets = []
    if type(obj['Top Tweets']) == str:
        new_top_tweets = re.sub(r"\<datasketch\.minhash\.MinHash object at 0x[A-Za-z0-9]+\>\, ", "None,", obj['Top Tweets'])
        tweets = ast.literal_eval(new_top_tweets)
    top_tweets = []
    for tweet in tweets:
        tdict = dict({"tweet_text": tweet[1],
                      "tid": tweet[2],
                      "uid": tweet[3],
                      "total_likes": tweet[6],
                      "total_shares": tweet[5],
                      "bot_counts": tweet[4]})
        top_tweets.append(tdict)
    obj['Top Tweets'] = top_tweets

    # modify top links
    links = []
    if type(obj["Top Links"]) == str:
        links = ast.literal_eval(obj['Top Links'])
    top_links = []
    for link in links:
        ldict = dict({"link": link[0],
                      "total_likes": link[3],
                      "total_shares": link[2],
                      "bot_counts": link[1]})
        top_links.append(ldict)
    obj['Top Links'] = top_links

    return obj

for country in non_en_files:
    filename3 = folder_location3 + "{}_{}_non_en_topic_clusters.csv".format(week_str,country)
    filename3_json = folder_location3 + "{}_{}_non_en_topic_clusters.json".format(week_str,country)
    df = pd.read_csv(filename3)
    if "Topic_History" not in df.columns:
        df["Topic_History"] = "{}"
    if df.empty:
        continue
    else:
        df["Topic_Type"] = df.apply(lambda row: calc_Topic_Type(row["Topic_History"]), axis=1)

    df = df.sort_values(by=['Likes Count', 'Shares Count', "Bot Count"], ascending=False)
    modified = json.loads(df.to_json(orient="records"), object_hook=default_handler)
    open(filename3_json,'w').write(json.dumps(modified))
    for folder_n in language_to_file_map[country]:
        destination_file = "/home/sid/CIPS/Results_merged/{}/{}_{}_non_en_topic_clusters.json".format(folder_n,week_str,country)
        if not os.path.exists("../Results_merged/{}/".format(folder_n)):
            os.makedirs("../Results_merged/{}/".format(folder_n))
        with open(destination_file,'w') as f1:
            f1.write(json.dumps(modified)) 


for country in en_files:
    filename3 = folder_location3 + "{}_{}_en_topic_clusters.csv".format(week_str,country)
    filename3_json = folder_location3 + "{}_{}_en_topic_clusters.json".format(week_str,country)
    df = pd.read_csv(filename3)
    if df.empty:
        continue
    if "Topic_History" not in df.columns:
        df["Topic_History"] = "{}"
    df["Topic_Type"] = df.apply(lambda row: calc_Topic_Type(row["Topic_History"]), axis=1)

    df = df.sort_values(by=['Likes Count', 'Shares Count', "Bot Count"], ascending=False)
    modified = json.loads(df.to_json(orient="records"), object_hook=default_handler)
    open(filename3_json,'w').write(json.dumps(modified))
    for folder_n in language_to_file_map[country]:
        destination_file = "../Results_merged/{}/{}_{}_en_topic_clusters.json".format(folder_n,week_str,country)
        if not os.path.exists("../Results_merged/{}/".format(folder_n)):
            os.makedirs("../Results_merged/{}/".format(folder_n))
        with open(destination_file,'w') as f1:
            f1.write(json.dumps(modified)) 

