import numpy as np
from matplotlib import pyplot as plt

import platform
import warnings

from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data
from modules.gen_freq_domain_data import gen_freq_domain_data


def plot_waveform_and_freq_response(
        data_normalized,
        amp_normalized,
        freq,
        fs,
        plot_pause,
        view_range,
        dbref,
        A
):
    # =======================================================
    # === Microphone入力音声ストリームデータ プロット関数 ===
    # =======================================================
    # data_normalized : 時間領域波形データ(正規化済)
    # amp_normalized : 周波数特性データ
    # freq : 周波数領域 軸データ
    # fs : フレームサイズ[sampling data count/frame]
    # plot_pause : グラフリアルタイム表示のポーズタイム[s]
    # view_range : 時間領域波形グラフ X軸表示レンジ[sample count]
    # dbref : デシベル基準値
    # A : 聴感補正(A特性)の有効(True)/無効(False)設定

    # フォント種別、およびサイズ設定
    plt.rcParams['font.size'] = 14
    plt.rcParams['font.family'] = 'Times New Roman'

    # 目盛内側化
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # 軸ラベル設定
    plt.xlabel('Sample Count')
    plt.ylabel('Amplitude')
    wave_fig.set_xlabel('Sample Count')
    wave_fig.set_ylabel('Amplitude')
    fft_fig.set_xlabel('Frequency [Hz]')

    if (dbref > 0) and not (A):
        fft_fig.set_ylabel('Amplitude [dB spl]')
    elif (dbref > 0) and (A):
        fft_fig.set_ylabel('Amplitude [dB spl(A)]')
    else:
        fft_fig.set_ylabel('Amplitude')

    # スケール設定
    wave_fig.set_xlim(0, view_range)
    wave_fig.set_ylim(-1, 1)
    wave_fig.set_yticks([-1, -0.5, 0, 0.5, 1])

    # fft_fig.set_xscale("log")
    fft_fig.set_xlim(0, 5000)
    fft_fig.set_ylim(-10, 90)
    fft_fig.set_yticks(np.arange(0, 100, 20))

    # plot.figure.tight_layout()実行時の「UserWarning: The figure layout has
    # changed to tight」Warning文の抑止
    warnings.simplefilter('ignore', UserWarning)

    # レイアウト設定
    fig.tight_layout()

    # 時間領域波形グラフプロット
    wave_fig.plot(data_normalized, color="blue")

    # 周波数特性グラフプロット
    fft_fig.plot(freq, amp_normalized, color="dodgerblue")

    plt.pause(plot_pause)

    fft_fig.cla()
    wave_fig.cla()


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート[sampling data count/s)]
    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定
    plot_pause = 0.0001     # グラフリアルタイム表示のポーズタイム[s]
    view_range = 2048       # 時間領域波形グラフ X軸表示レンジ[sample count]

    # フレームサイズ[sampling data count/frame]
    if platform.machine() == "armv7l":  # ARM32bit向け(Raspi等)
        fs = 512
    elif platform.machine() == "x86_64":  # Intel64bit向け
        # 4096以下の場合、「OSError: [Errno -9981] Input overflowed」が発生したため、16384としている
        fs = 16384
    elif platform.machine() == "AMD64":  # AMD64bit向け
        # グラフが正常表示されなかったため、16384としている
        fs = 16384
    else:
        fs = 1024
    print("\nFrameSize[sampling data count/frame] = ", fs, "\n")
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(index, mic_mode, samplerate, fs)
    # pa : pyaudioクラスオブジェクト
    # stream : マイク入力音声ストリーム

    # === 時間領域波形と周波数特性向けの2つのグラフ領域を作成
    fig = plt.figure()
    wave_fig = fig.add_subplot(2, 1, 1)
    fft_fig = fig.add_subplot(2, 1, 2)

    # === 時間領域波形 & 周波数特性リアルタイムプロット ===
    # キーボードインタラプトあるまでループ処理継続
    while True:
        try:
            # === 時間領域波形データ生成 ===
            data_normalized = gen_time_domain_data(stream, fs)
            # data_normalized   : 時間領域 波形データ(正規化済)

            # === 周波数特性データ生成 ===
            spectrum, amp_normalized, phase, freq = gen_freq_domain_data(
                data_normalized, fs, samplerate, dbref, A
            )
            # spectrum          : 周波数特性データ(複素数データ)
            # amp_normalized    : 周波数特性 振幅データ(正規化済)
            # phase             : 周波数特性 位相データ
            # freq              : 周波数特性 X軸向けデータ

            # === グラフプロット ===
            plot_waveform_and_freq_response(
                data_normalized,
                amp_normalized,
                freq,
                fs,
                plot_pause,
                view_range,
                dbref,
                A)

        except KeyboardInterrupt:   # Ctrl+c で終了
            break

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

    print("=================")
    print("= Main Code END =")
    print("=================\n")
