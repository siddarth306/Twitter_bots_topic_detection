week=14 
data = pd.read_csv("/home/sid/CIPS/Twitter_bots_topic_detection/InputData/week15/week15.csv") 
data2 = data[data["language"]=="en"] 
data2_grouped = data2.groupby("country") 
data_dict = {} 
for idx, df in data2_grouped: 
    key = df.iloc[0]["country"] 
    data_dict[key] = df 
if len(data_dict) != 3: 
    print("Error!!") 
f1 = open("/home/sid/CIPS/Twitter_bots_topic_detection/IntermediateData_coronavirus/week15/week15_all_tweets_preprocessing.pkl","wb") 
pickle.dump(data_dict,f1) 
f1.close() 


import pandas as pd
import pickle
week = 13
f1 = open("/home/sid/CIPS/Twitter_bots_topic_detection/IntermediateData_coronavirus/week{}/week{}_all_coronvirus_tweets_preprocessing.pkl".format(week,week),"rb")
data_luis = pickle.load(f1)
f1.close()
f2 = open("/home/sid/CIPS/Twitter_bots_topic_detection/IntermediateData_coronavirus/week{}/week{}_all_coronvirus_tweets_preprocessing_cips.pkl".format(week,week),"rb")
data_cips = pickle.load(f2)
f2.close()

combined_dict = {}
for country in ["usa","uk","eu"]:    
    combined_df = pd.DataFrame()
    combined_df = combined_df.append(data_cips[country], ignore_index = True)
    combined_df = combined_df.append(data_luis[country], ignore_index = True)
    combined_dict[country] = combined_df

f3 = open("/home/sid/CIPS/Twitter_bots_topic_detection/IntermediateData_coronavirus/week{}/week{}_all_coronvirus_tweets_preprocessing_combined.pkl".format(week,week),"wb")
pickle.dump(combined_dict, f3)
f3.close()



import pandas as pd 
countries = ["usa","uk","eu"] 
weeks = range(1,16) 
path = "/home/sid/CIPS/Twitter_bots_topic_detection/ResultData_coronavirus/week{}/week{}_{}_en_topic_clusters.csv" 
for ct in countries: 
    data_df = pd.DataFrame() 
    for wk in weeks: 
        try: 
            country_df  = pd.read_csv(path.format(wk,wk, ct)) 
            data_df = data_df.append(country_df, ignore_index = True) 
        except FileNotFoundError: 
            continue 
    data_df.to_csv("coronavirus_{}_all_weeks.csv".format(ct), index=False) 


path = "/home/sid/CIPS/Twitter_bots_topic_detection/InputData_coronavirus/Week{}.csv"
import pandas as pd
import pickle
bots_list = set()
bots_f = open("/home/sid/CIPS/Twitter_bots_topic_detection/InputData/clean_blot_list.pickle", "rb")
bots_ids = list(pickle.load(bots_f))
bot_set = set([int(float(i)) for i in bots_ids[1:]])
for wk in range(2,13):
    try:
        data = pd.read_csv(path.format(wk))
    except FileNotFoundError:
        continue
    if wk == 6:
        bots_list.update(set(data["uid"].unique()).intersection(bot_set))
    else:
        bots_list.update(list(data["uid"].unique()))
    
path2 = "/home/sid/CIPS/Twitter_bots_topic_detection/IntermediateData_coronavirus/week{}/week{}_all_coronvirus_tweets_preprocessing.pkl"
import pandas as pd
import pickle
for wk in range(13,16):
    with open(path2.format(wk,wk), "rb") as f1:
        data = pickle.load(f1)
        for _,df in data.items():
            bots_list.update(list(df["uid"].unique()))
            
            
            
            
#Get frequent coronavirus phrases

import pandas as pd
np_ne_path = "/home/sid/Downloads/w13_14_15_top_ne_np/w{}_{}.csv"
corona_phrases_df = pd.read_csv("/home/sid/CIPS/Twitter_bots_topic_detection/InputData/coronavirus-nouns-v3.csv")
corona_phrases_set = set(corona_phrases_df["Phrase"].to_list())
country_dict = {}
from collections import defaultdict
for ct in ["usa","uk","eu"]:
    for wk in [13,14,15]:
        data = pd.read_csv(np_ne_path.format(wk,ct), header=None)
        data.columns = ["phrase","count"]
        data_dict = defaultdict(int)
        for idx,row in data.iterrows():
            if row["phrase"] in corona_phrases_set:
                data_dict[row["phrase"]] += row["count"]
    country_dict[ct] = data_dict
    
        
           
