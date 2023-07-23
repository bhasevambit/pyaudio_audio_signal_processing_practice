import numpy as np
from matplotlib import pyplot as plt

import os
import datetime
import warnings


def gen_graph_figure():
    # =========================================================
    # === 時間領域波形 & 周波数特性向けのグラフ領域作成関数 ===
    # =========================================================
    fig = plt.figure()
    wave_fig = fig.add_subplot(2, 1, 1)
    freq_fig = fig.add_subplot(2, 1, 2)

    # 上下左右にグラフ目盛線を付与
    wave_fig.yaxis.set_ticks_position('both')
    wave_fig.xaxis.set_ticks_position('both')
    freq_fig.yaxis.set_ticks_position('both')
    freq_fig.xaxis.set_ticks_position('both')

    return fig, wave_fig, freq_fig


def plot_time_and_freq_realtime(
    fig,
    wave_fig,
    freq_fig,
    data_normalized,
    t,
    amp_normalized,
    freq,
    plot_pause,
    view_range,
    dbref,
    A
):
    # =======================================================
    # === Microphone入力音声ストリームデータ プロット関数 ===
    # =======================================================
    # fig               : リアルタイム更新対象のグラフfigure
    # wave_fig          : リアルタイム更新対象の時間領域波形グラフfigure
    # freq_fig          : リアルタイム更新対象の周波数特性グラフfigure
    # data_normalized   : 時間領域 波形データ(正規化済)
    # t                 : 時間領域 X軸向けデータ [ms]
    # amp_normalized    : 周波数特性 振幅データ(正規化済)
    # freq              : 周波数特性 X軸向けデータ
    # fs                : フレームサイズ [sampling data count/frame]
    # plot_pause        : グラフリアルタイム表示のポーズタイム [s]
    # view_range        : 時間領域波形グラフ X軸表示レンジ [sample count]
    # dbref             : デシベル基準値
    # A                 : 聴感補正(A特性)の有効(True)/無効(False)設定

    # フォント種別、およびサイズ設定
    plt.rcParams['font.size'] = 14
    plt.rcParams['font.family'] = 'Times New Roman'

    # 目盛内側化
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # 時間領域波形 軸ラベル設定
    wave_fig.set_xlabel('Time [ms]')
    wave_fig.set_ylabel('Amplitude')

    # 周波数特性 軸ラベル設定
    freq_fig.set_xlabel('Frequency [Hz]')
    if (dbref > 0) and not (A):
        freq_fig.set_ylabel('Amplitude [dB spl]')
    elif (dbref > 0) and (A):
        freq_fig.set_ylabel('Amplitude [dB spl(A)]')
    else:
        freq_fig.set_ylabel('Amplitude')

    # 時間領域波形 軸目盛り設定
    wave_fig.set_xlim(0, view_range)
    wave_fig.set_ylim(-1, 1)
    wave_fig.set_yticks([-1, -0.5, 0, 0.5, 1])

    # 周波数特性 軸目盛り設定
    freq_fig.set_xlim(0, 5000)
    freq_fig.set_ylim(-10, 90)
    freq_fig.set_yticks(np.arange(0, 100, 20))

    # plot.figure.tight_layout()実行時の「UserWarning: The figure layout has
    # changed to tight」Warning文の抑止
    warnings.simplefilter('ignore', UserWarning)

    # レイアウト設定
    fig.tight_layout()

    # 時間領域波形グラフプロット
    wave_fig.plot(t, data_normalized, color="blue")

    # 周波数特性グラフプロット
    freq_fig.plot(freq, amp_normalized, color="dodgerblue")

    plt.pause(plot_pause)

    freq_fig.cla()
    wave_fig.cla()


def plot_time_and_freq_fixed_period(
    fig,
    wave_fig,
    freq_fig,
    t,
    data_normalized,
    freq,
    amp_normalized,
    view_range,
    dbref,
    A
):
    # ====================================================
    # === 時間領域波形 & 周波数特性 グラフプロット関数 ===
    # ====================================================
    # fig               : リアルタイム更新対象のグラフfigure
    # wave_fig          : リアルタイム更新対象の時間領域波形グラフfigure
    # freq_fig          : リアルタイム更新対象の周波数特性グラフfigure
    # data_normalized   : 時間領域 波形データ(正規化済)
    # t                 : 時間領域 X軸向けデータ [ms]
    # amp_normalized    : 周波数特性 振幅データ(正規化済)
    # freq              : 周波数特性 X軸向けデータ
    # fs                : フレームサイズ [sampling data count/frame]
    # view_range        : 時間領域波形グラフ X軸表示レンジ [sample count]
    # dbref             : デシベル基準値
    # A                 : 聴感補正(A特性)の有効(True)/無効(False)設定
    print("Graph Plot START")

    # フォント種別、およびサイズ設定
    plt.rcParams['font.size'] = 14
    # plt.rcParams['font.family'] = 'Times New Roman'   #
    # Raspiへの対応のためにフォント指定無効化

    print("  - Graph Axis Setting START")

    # 目盛内側化
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    print("  - Graph Axis Setting END")

    # 軸ラベル設定
    wave_fig.set_xlabel('Time [s]')
    wave_fig.set_ylabel('Amplitude')
    freq_fig.set_xlabel('Frequency [Hz]')

    if (dbref > 0) and not (A):
        freq_fig.set_ylabel('Amplitude [dB spl]')
    elif (dbref > 0) and (A):
        freq_fig.set_ylabel('Amplitude [dB spl(A)]')
    else:
        freq_fig.set_ylabel('Amplitude')

    print("  - Graph AxisLable Setting END")

    # スケール設定
    freq_fig.set_xticks(np.arange(0, 25600, 1000))
    freq_fig.set_xlim(0, 5000)
    freq_fig.set_ylim(
        np.max(amp_normalized) - 100,
        np.max(amp_normalized) + 10)
    print("  - Graph Scale Setting END")

    # 時間領域波形データプロット
    print("  - Time Waveform Graph DataPlot START")
    wave_fig.plot(
        t,
        data_normalized,
        label='Time waveform',
        lw=1,
        color="blue")
    print("  - Time Waveform Graph DataPlot END")

    # 周波数特性データプロット
    print("  - Freq Response Graph DataPlot START")
    freq_fig.plot(
        freq,
        amp_normalized,
        label='Amplitude',
        lw=1,
        color="dodgerblue")
    print("  - Freq Response Graph DataPlot END")

    # レイアウト設定
    fig.tight_layout()
    print("  - Graph Layout Setting END")

    # グラフ保存
    print("  - Graph File Save START")
    now_grf_Tnf = datetime.datetime.now()

    grf_dirname = 'graph/'
    if not os.path.isdir(grf_dirname):
        os.mkdir(grf_dirname)

    filename_grf_Tnf = grf_dirname + 'time-waveform_and_freq-response_' + \
        now_grf_Tnf.strftime('%Y%m%d_%H%M%S') + '.png'
    plt.savefig(filename_grf_Tnf)
    print("  - Graph File Save END")
    plt.close()

    print("Graph Plot END\n")
