from matplotlib import pyplot as plt

import datetime


def plot_general(t, x, label, xlabel, ylabel, figsize, xlim, ylim, xlog, ylog):
    # ===========================================
    # === 汎用プロット関数(1プロット重ね書き) ===
    # ===========================================

    # フォントの種類とサイズを設定
    plt.rcParams['font.size'] = 14
    # plt.rcParams['font.family'] = 'Times New Roman'
    # Raspiへの対応のためにフォント指定無効化

    # 目盛内側化
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # Subplot設定、およびグラフの目盛線を付与
    fig = plt.figure(figsize=figsize)
    ax1 = fig.add_subplot(111)
    ax1.yaxis.set_ticks_position('both')
    ax1.xaxis.set_ticks_position('both')

    # 軸ラベル設定
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)

    # スケールを設定
    if xlim != [0, 0]:
        ax1.set_xlim(xlim[0], xlim[1])
    if ylim != [0, 0]:
        ax1.set_ylim(ylim[0], ylim[1])

    # 対数スケール化
    if xlog == 1:
        ax1.set_xscale('log')
    if ylog == 1:
        ax1.set_yscale('log')

    # プロット
    for i in range(len(x)):
        ax1.plot(t[i], x[i], label=label[i], lw=1)
    ax1.legend()

    # レイアウト設定
    fig.tight_layout()

    # グラフ保存
    now = datetime.datetime.now()
    filename = 'graph_' + \
        now.strftime('%Y%m%d_%H%M%S') + '.png'
    plt.savefig(filename)
    plt.close()

    return 0
