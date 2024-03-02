import pandas as pd

# Read csv into pd df
'''
Get the data from the write & read csv files into a pandas df.
returns: all logs from write&read lmds sorted by e_id.
'''
def prep_logs_data(write_csv_path, read_csv_path, run_id):
    w_raw_df = pd.read_csv(write_csv_path)
    r_raw_df = pd.read_csv(read_csv_path)

    # filter log values by run_id
    w_fil_df = w_raw_df[w_raw_df["run_id"] == run_id]
    r_fil_df = r_raw_df[r_raw_df["run_id"] == run_id]
    w_df = w_fil_df.sort_values(by='key_size')
    r_df = r_fil_df.sort_values(by='key_size')

    # Concat w & r dfs & save as csv
    full_df = pd.concat([w_df, r_df], ignore_index=True)
        # Save full_df as file format: '{ds}_{run_id}'
    
    return w_df, r_df

'''
latency = readfn_start_time - put_time
return: A array with arrays of latencies for each key size
'''
def calc_latency(w_csv_path, r_csv_path, run_id):
    w_df, r_df = prep_logs_data(w_csv_path, r_csv_path, run_id)

    # Array of ksizes
    ksizes_list = w_df["key_size"].unique()
    ksizes_list.sort()

    overall_latencies = []
    # Per ksize logic
    for i in ksizes_list:
        ksize_latencies = [] # array with each iter latency for that ksize
        
        tmpw_df = w_df[w_df["key_size"] == i]
        tmpr_df = r_df[r_df["key_size"] == i]
        
        for j in tmpw_df["e_id"]: # get latency for each event (e_id)
            w_time = tmpw_df.loc[tmpw_df["e_id"] == j, "put_time"].iat[0]
            try:
                r_time = tmpr_df.loc[tmpr_df["e_id"] == j, "exec_start_time"].iat[0]
            except:
                print(f"Event id {j} not received by read-lmd")
            # get latency for one event
            latency = r_time - w_time
            ksize_latencies.append(latency)
        # print(f"Ksize {i}: {ksize_latencies}")
        overall_latencies.append(ksize_latencies)

    return overall_latencies


# Filter by run_id


# Sort by key_size


# Gen Latency arr & key size arr