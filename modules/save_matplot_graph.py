from matplotlib import pyplot as plt

import os
import datetime


def save_matplot_graph():
    # ======================
    # === グラフ保存関数 ===
    # ======================
    print("Graph File Save START")

    now = datetime.datetime.now()

    dirname = 'graph/'
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    filename = dirname + 'time-waveform_and_freq-response_' + \
        now.strftime('%Y%m%d_%H%M%S') + '.png'

    # matplotlibグラフをpngファイルとして保存
    plt.savefig(filename)
    plt.close()

    print("Graph File Save END\n")
