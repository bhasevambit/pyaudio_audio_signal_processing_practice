import numpy as np
from matplotlib import pyplot as plt

import warnings


def plot_waveform_and_freq_response(
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
