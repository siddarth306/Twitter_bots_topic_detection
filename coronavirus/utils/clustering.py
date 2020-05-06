from collections import defaultdict
from tqdm import tqdm

def calculate_topics_by_hashtags(hashtags, hashtags_phrases, minPoints, epsilon):

    if len(hashtags) < 100:
        epsilon = 0.2
        minPoints = 1
    elif len(hashtags) < 500:
        minPoints = 1
    else:
        minPoints=2

    hashtags_adj_list = defaultdict(set)
    print("\t- Calculating Neighbors")
    for idx, (ht1,_) in tqdm(enumerate(hashtags)):
        for (ht2,_) in hashtags[idx+1:]:
            hash_index_num = len(hashtags_phrases[ht1].intersection(hashtags_phrases[ht2])) 
            hash_index_den = len(hashtags_phrases[ht1].union(hashtags_phrases[ht2]))
            if hash_index_den != 0 and hash_index_num / hash_index_den >= epsilon:
                hashtags_adj_list[ht1].add(ht2)
                hashtags_adj_list[ht2].add(ht1)

    core_set = set()

    print("\t-Calculating core points")
    for ht, neighbors in tqdm(hashtags_adj_list.items()):
        if len(neighbors) >= minPoints:
            core_set.add(ht)
    
    visited = set()

    print("\t-Clustering core points")
    all_clusters = []
    for ht in tqdm(core_set):
        if not (ht in visited):
            cluster = []
            visited.add(ht)
            queue = [ht]
            while len(queue) != 0:
                cluster_member = queue.pop(0)
                cluster.append(cluster_member)
                for n in hashtags_adj_list[cluster_member]:
                    if n in core_set and not (n in visited):
                        queue.append(n)
                        visited.add(n)
            all_clusters.append(cluster)

    return all_clusters


