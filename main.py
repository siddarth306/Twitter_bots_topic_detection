import all_cluster
import sys
import os

BASE_DIR = os.getcwd()
INPUT_DIR = BASE_DIR + "/InputData/"
INTERM_DIR = BASE_DIR + "/IntermediateData/"
RESULT_DIR = BASE_DIR + "/ResultData/"

if __name__ == "__main__":
    args = sys.argv
    if args[1] == "week_clusters":
        week_no = sys.argv[2]
        week_str = "week" + str(week_no)
        tool_config = {}
        tool_config["week_str"] = week_str
        tool_config["epsilon"] = 0.6
        tool_config["minPoints"] = 2

        interm_file_loc = INTERM_DIR + week_str + "/"
        input_file_loc = INPUT_DIR + week_str + "/"
        result_file_loc = RESULT_DIR + week_str + "/"

        if not os.path.exists(interm_file_loc):
            os.makedirs(interm_file_loc)

        if not os.path.exists(result_file_loc):
            os.makedirs(result_file_loc)

        tool_config["input_out_file_loc"] = INPUT_DIR + "{}"
        tool_config["inter_file_loc"] = interm_file_loc + "{}"
        tool_config["result_file_loc"] = result_file_loc + "{}"
        tool_config["input_file_loc"] = input_file_loc + "{}"
        tool_config["all_lang"] = "all_countries"
        cluster_results = all_cluster.calculate_clusters(tool_config)
    elif args[1] == "topic_linking":
        pass
    else:
        pass
    import pdb; pdb.set_trace()
