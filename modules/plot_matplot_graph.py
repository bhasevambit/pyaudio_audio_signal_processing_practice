import numpy as np
from matplotlib import pyplot as plt

import warnings


def gen_graph_figure():
    # ==========================
    # === グラフ領域作成関数 ===
    # ==========================

    fig = plt.figure()
    sub_fig1 = fig.add_subplot(2, 1, 1)
    sub_fig2 = fig.add_subplot(2, 1, 2)

    # 上下左右にグラフ目盛線を付与
    sub_fig1.yaxis.set_ticks_position('both')
    sub_fig1.xaxis.set_ticks_position('both')
    sub_fig2.yaxis.set_ticks_position('both')
    sub_fig2.xaxis.set_ticks_position('both')

    return fig, sub_fig1, sub_fig2


def plot_time_and_freq(
    fig,
    wave_fig,
    freq_fig,
    data_normalized,
    t,
    amp_normalized,
    freq,
    view_range,
    dbref,
    A,
    plot_pause
):
    # ====================================================
    # === 時間領域波形 & 周波数特性 グラフプロット関数 ===
    # ====================================================
    # fig               : matplotlib グラフfigure
    # wave_fig          : matplotlib 時間領域波形グラフfigure
    # freq_fig          : matplotlib 周波数特性グラフfigure
    # data_normalized   : 時間領域 波形データ(正規化済)
    # t                 : 時間領域 X軸向けデータ [ms]
    # amp_normalized    : 周波数特性 振幅データ(正規化済)
    # freq              : 周波数特性 X軸向けデータ
    # view_range        : 時間領域波形グラフ X軸表示レンジ [sample count]
    # dbref             : デシベル基準値
    # A                 : 聴感補正(A特性)の有効(True)/無効(False)設定
    # plot_pause        : グラフ表示のpause時間 [s] (非リアルタイムモード(指定時間録音)の場合は"-1"を設定)

    # フォントサイズ設定
    plt.rcParams['font.size'] = 10

    # 目盛内側化
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # 時間領域波形 軸ラベル設定
    if plot_pause == -1:
        # 録音時間指定モードの場合
        wave_fig.set_xlabel('Time [s]')
    else:
        # リアルタイムモードの場合
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

    # 時間領域波形データプロット
    wave_fig.plot(
        t,
        data_normalized,
        label='Time Waveform',
        lw=1,
        color="blue")

    # 周波数特性データプロット
    freq_fig.plot(
        freq,
        amp_normalized,
        label='Frequency Response',
        lw=1,
        color="dodgerblue")

    if plot_pause != -1:
        # リアルタイムモードの場合、matplotlibグラフを更新
        plt.pause(plot_pause)

        freq_fig.cla()
        wave_fig.cla()


def plot_time_and_spectrogram(
    data_normalized,
    t,
    view_range,
    freq_spctrgrm,
    time_spctrgrm,
    spectrogram
):
    # ==========================================================
    # === 時間領域波形 & スペクトログラム グラフプロット関数 ===
    # ==========================================================
    # data_normalized   : 時間領域 波形データ(正規化済)
    # t                 : 時間領域 X軸向けデータ [ms]
    # view_range        : 時間領域波形グラフ X軸表示レンジ [sample count]
    # freq_spctrgrm     : Array of sample frequencies
    # time_spctrgrm     : Array of segment times
    # spectrogram       : Spectrogram

    # グラフfigure設定
    fig = plt.figure(figsize=[8, 7])
    # add_axesの引数パラメータは「left，bottom，width，height」
    axes_left_common = 0.12
    axes_height_spctrgrm = 0.5
    axes_height_wave = 0.25
    axes_bottom_spctrgrm = 0.1
    axes_bottom_wave = axes_bottom_spctrgrm + axes_height_spctrgrm + 0.1
    axes_width_spctrgrm = 0.89  # 時間領域波形とスペクトログラムの横軸メモリが合うように微調整
    axes_width_wave = 0.71  # 時間領域波形とスペクトログラムの横軸メモリが合うように微調整

    wave_fig = fig.add_axes(
        (
            axes_left_common,
            axes_bottom_wave,
            axes_width_wave,
            axes_height_wave
        )
    )
    spctrgrm_fig = fig.add_axes(
        (
            axes_left_common,
            axes_bottom_spctrgrm,
            axes_width_spctrgrm,
            axes_height_spctrgrm
        )
    )

    # フォントサイズ設定
    plt.rcParams['font.size'] = 10

    # 目盛内側化
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # 時間領域波形 軸ラベル設定
    wave_fig.set_xlabel('Time [s]')
    wave_fig.set_ylabel('Amplitude')

    # スペクトログラム 軸ラベル設定
    spctrgrm_fig.set_xlabel('Time [s]')
    spctrgrm_fig.set_ylabel('Frequency [Hz]')

    # 時間領域波形 軸目盛り設定
    wave_fig.set_xlim(0, view_range)
    wave_fig.set_ylim(-1, 1)
    wave_fig.set_yticks([-1, -0.5, 0, 0.5, 1])

    # スペクトログラム 軸目盛り設定
    spctrgrm_fig.set_xlim(0, view_range)
    spctrgrm_fig.set_ylim(0, 2000)  # 0 ～ 2000[Hz]の範囲

    # plot.figure.tight_layout()実行時の「UserWarning: The figure layout has
    # changed to tight」Warning文の抑止
    warnings.simplefilter('ignore', UserWarning)

    # レイアウト設定
    fig.tight_layout()

    # 時間領域波形データプロット
    wave_fig.plot(
        t,
        data_normalized,
        label='Time Waveform',
        lw=1,
        color="blue"
    )

    # スペクトログラムデータプロット
    # スペクトログラムデータはログスケール表示 (= 10 * log10(spectrogram))
    spctrgrm_im = spctrgrm_fig.pcolormesh(
        time_spctrgrm,
        freq_spctrgrm,
        10 * np.log10(spectrogram),
        cmap='jet'
    )

    # カラーバー設定
    cbar = fig.colorbar(spctrgrm_im)
    cbar.set_label("???")
