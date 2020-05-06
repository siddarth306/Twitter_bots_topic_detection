import sys
import os



BASE_DIR = os.getcwd()
APPS_CONFIG = {
    "reports": {
                "input_dir": BASE_DIR + "/reports/InputData/",
                "interm_dir": BASE_DIR + "/reports/IntermediateData/",
                "result_dir": BASE_DIR + "/reports/ResultData/",
                "misc_dir": BASE_DIR + "/reports/MiscData/"
                },
                
    "coronavirus": {
                "input_dir": BASE_DIR + "/coronavirus/InputData/",
                "interm_dir": BASE_DIR + "/coronavirus/IntermediateData/",
                "result_dir": BASE_DIR + "/coronavirus/ResultData/",
                "misc_dir": BASE_DIR + "/coronavirus/MiscData/"
                },    
}

week_map = {
    1: ["12/04/2019", "12/10/2019"],
    2: ["12/11/2019", "12/17/2019"],
    3: ["12/18/2019", "12/24/2019"],
    4: ["01/05/2020", "01/11/2020"],
    5: ["01/12/2020", "01/17/2020"],
    6: ["01/18/2020", "01/24/2020"],
    7: ["02/04/2020", "02/10/2020"],
    8: ["02/11/2020", "02/17/2020"],
    9: ["02/18/2020", "02/24/2020"],
    10:["02/25/2020", "03/03/2020"],
    11:["03/03/2020", "03/10/2020"],
    12:["03/11/2020", "03/18/2020"],
    13:["03/19/2020", "03/25/2020"],
    14:["03/26/2020", "04/01/2020"],
    15:["04/02/2020" , "04/08/2020"]

}
if __name__ == "__main__":
    args = sys.argv
    app = args[1]
    if app == "reports":
        week_no = sys.argv[2]
        from reports import all_cluster
        week_str = "week" + str(week_no)

        interm_file_loc = APPS_CONFIG[app]["interm_dir"] + week_str + "/"
        input_file_loc = APPS_CONFIG[app]["input_dir"] + week_str + "/"
        result_file_loc = APPS_CONFIG[app]["result_dir"] + week_str + "/"

        if not os.path.exists(interm_file_loc):
            os.makedirs(interm_file_loc)

        if not os.path.exists(result_file_loc):
            os.makedirs(result_file_loc)

        tool_config = {
            "week": int(week_no),
            "week_str": week_str,
            "epsilon": 0.5,
            "minPoints": 2,
            "date": week_map[int(week_no)],
            "input_out_file_loc": APPS_CONFIG[app]["input_dir"] + "{}",
            "misc_file_loc": APPS_CONFIG[app]["misc_dir"] + "{}",
            "inter_file_loc": interm_file_loc + "{}",
            "result_file_loc": result_file_loc + "{}",
            "input_file_loc": input_file_loc + "{}",
            "all_lang": "all_countries",
        }

        cluster_results = all_cluster.calculate_clusters(tool_config)

    elif app == "coronavirus":

        from coronavirus import all_cluster
        week_no = sys.argv[2]
        week_str = "week" + str(week_no)

        interm_file_loc = APPS_CONFIG[app]["interm_dir"] + week_str + "/"
        input_file_loc = APPS_CONFIG[app]["input_dir"] + week_str + "/Week{}.csv".format(week_no) 
        result_file_loc = APPS_CONFIG[app]["result_dir"] + week_str + "/"

        if not os.path.exists(interm_file_loc):
            os.makedirs(interm_file_loc)

        if not os.path.exists(result_file_loc):
            os.makedirs(result_file_loc)

        tool_config = {
            "week": int(week_no),
            "week_str": week_str,
            "epsilon": 0.5,
            "minPoints": 2,
            "date": week_map[int(week_no)],
            "input_out_file_loc": APPS_CONFIG[app]["input_dir"] + "{}",
            "misc_file_loc": APPS_CONFIG[app]["misc_dir"] + "{}",
            "inter_file_loc": interm_file_loc + "{}",
            "result_file_loc": result_file_loc + "{}",
            "input_file_loc": input_file_loc,
            "all_lang": "all_countries",
        }

        cluster_results = all_cluster.calculate_clusters(tool_config)
 
    else:
        print("Enter a valid app to run")
        pass
