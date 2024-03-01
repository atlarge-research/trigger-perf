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
latency = readfn_start_time - s3_put_time
'''
def calc_latency(w_csv_path, r_csv_path):
    w_df, r_df = prep_logs_data(w_csv_path, r_csv_path)
    
    s3_put_times = w_df['put_time']
    rlmd_start_times = r_df['exec_start_time']
    print(rlmd_start_times)
    print(s3_put_times)
    latencies = []
    for i in range(0,len(rlmd_start_times)):
        latency = rlmd_start_times[i] - s3_put_times[i]
        latencies.append(latency)

    return latencies


# Filter by run_id


# Sort by key_size


# Gen Latency arr & key size arr