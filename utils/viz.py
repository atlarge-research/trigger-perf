import matplotlib.pyplot as plt
import numpy as np


# need: s3_put_time, readfn_start_time, Key, ksize, vsize

'''
input: x_values (key sizes) & y_values (latencies)
'''
def ksize_vs_latency(x_vals, y_vals):
    pass


'''
input: x_values (value sizes) & y_values (latencies)
'''
def vsize_vs_latency():
    pass

def gen_line_graph(x_vals, y_vals, x_label="x-axis", y_label="y-axis", title="Line graph", despath=None):
    plt.plot(x_vals, y_vals, label='Keysize vs Latency')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.savefig(despath)


'''
input: 2d array of data, run_id, x_axis_labels
'''
def gen_box_plot(data, run_id, x_axis_labels):
    plt.boxplot(data)
    # plt.xticks(x_axis_labels)
    plt.title('Latency plot')
    plt.xlabel('Columns')
    plt.ylabel('Latency (ms)')
    despath = f"./plots/{run_id}.png"
    plt.savefig(despath) # change this to save fig as {run_id}_{ds}.png
    



def master_viz_gen():

    pass

