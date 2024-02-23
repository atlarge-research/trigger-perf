import matplotlib.pyplot as plt


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




def master_viz_gen():

    pass

x_values = [1, 2, 3, 4, 5]
y_values = [10, 12, 5, 8, 20]

# Generate and display the line graph
gen_line_graph(x_values, y_values,"keys", "latency", "ksize_vs_latency","../plots/ksize_vs_latency.png")