import pyaudio
import scipy
import numpy as np
from matplotlib import pyplot as plt
import math

import platform
import os
import datetime
import soundfile as sf

from modules.get_mic_index import get_mic_index
from modules.a_weighting import a_weighting


def record(index, mic_mode, samplerate, fs, time):
    # ============================================
    # === Microphone入力音声レコーディング関数 ===
    # ============================================
    # index : 使用するマイクのdevice index
    # mic_mode : mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]
    # time : 録音時間[s]

    pa = pyaudio.PyAudio()

    # ストリームの開始
    data = []
    dt = 1 / samplerate

    stream = pa.open(
        format=pyaudio.paInt16,
        # pyaudio.paInt16 = 16bit量子化モード (音声時間領域波形の振幅を-32767～+32767に量子化)
        channels=mic_mode,
        rate=samplerate,
        input=True,
        input_device_index=index,
        frames_per_buffer=fs
    )

    # フレームサイズ毎に音声を録音していくループ
    print("Recording START")
    i = 0

    for i in range(int(((time / dt) / fs))):
        erapsed_time = math.floor(((i * fs) / samplerate) * 100) / 100
        print("  - Erapsed Time[s]: ", erapsed_time)

        frame = stream.read(fs)
        data.append(frame)

    print("Recording STOP\n")

    # ストリームの終了
    stream.stop_stream()

    stream.close()
    pa.terminate()

    # データをまとめる処理
    # print("data(before joined) = ", data)
    data = b"".join(data)   # frame毎に、要素が分かれていたdataを、要素間でbyte列連結
    # print("data(after joined) = ", data)

    # データをNumpy配列に変換し、時間軸を作成
    # dataについては、16bit量子化であり、かつ正負符号を持つ事から、
    # ±32767(=±((2^16 / 2) - 1))の範囲にデータが入る事から、dataを((2^16 / 2) - 1)で割る事で、正規化している
    data = np.frombuffer(data, dtype="int16") / \
        float((np.power(2, 16) / 2) - 1)

    # tについては、numpy.arrange()を用いて、
    #   start : 0
    #   stop : (録音時間にしめるサンプリングデータ数 / フレームサイズ)の整数部 * フレームサイズ * サンプリング周期[s],
    #   step : サンプリング周期[s]
    # とし、配列を作っている
    t = np.arange(0, int(((time / dt) / fs)) * fs * dt, dt)

    return data, t


def calc_fft(data, samplerate, dbref, A):
    # ============================================
    # === フーリエ変換関数 (dB変換とA補正付き) ===
    # ============================================

    # 信号のフーリエ変換
    print("Fourier transform START")
    spectrum = scipy.fft.fft(data)

    # 振幅成分算出
    amp = np.sqrt((spectrum.real ** 2) + (spectrum.imag ** 2))
    print("  - Amplitude Caluculation END")

    # 振幅成分の正規化
    amp = amp / (len(data) / 2)
    print("  - Amplitude Normalization END")

    # 位相成分算出 & 位相をラジアンから度に変換
    phase = np.arctan2(spectrum.imag, spectrum.real)
    phase = np.degrees(phase)
    print("  - Phase Caluculation END")

    # 周波数軸を作成
    freq = np.linspace(0, samplerate, len(data))
    print("  - Frequency Axis generation END")

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        amp = 20 * np.log10(amp / dbref)

        # dB変換されていてAがTrueの時に聴感補正する
        if A:
            amp += a_weighting(freq)

    print("Fourier transform END\n")
    return spectrum, amp, phase, freq


def plot_time_and_freq(t, data, freq, amp, dbref, A):
    # ====================================================
    # === 時間領域波形 & 周波数特性 グラフプロット関数 ===
    # ====================================================
    print("Graph Plot START")

    # フォント種別、およびサイズ設定
    plt.rcParams['font.size'] = 14
    # plt.rcParams['font.family'] = 'Times New Roman'   #
    # Raspiへの対応のためにフォント指定無効化

    print("  - Graph Axis Setting START")

    # 目盛内側化
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # グラフ目盛線付与
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.yaxis.set_ticks_position('both')
    ax1.xaxis.set_ticks_position('both')
    ax2 = fig.add_subplot(212)
    ax2.yaxis.set_ticks_position('both')
    ax2.xaxis.set_ticks_position('both')

    print("  - Graph Axis Setting END")

    # 軸ラベル設定
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Amplitude')
    ax2.set_xlabel('Frequency [Hz]')

    if (dbref > 0) and not (A):
        ax2.set_ylabel('Amplitude [dB spl]')
    elif (dbref > 0) and (A):
        ax2.set_ylabel('Amplitude [dB spl(A)]')
    else:
        ax2.set_ylabel('Amplitude')

    print("  - Graph AxisLable Setting END")

    # スケール設定
    ax2.set_xticks(np.arange(0, 25600, 1000))
    ax2.set_xlim(0, 5000)
    ax2.set_ylim(np.max(amp) - 100, np.max(amp) + 10)
    print("  - Graph Scale Setting END")

    # 時間領域波形データプロット
    print("  - Time Waveform Graph DataPlot START")
    ax1.plot(t, data, label='Time waveform', lw=1, color="blue")
    print("  - Time Waveform Graph DataPlot END")

    # 周波数特性データプロット
    print("  - Freq Response Graph DataPlot START")
    ax2.plot(freq, amp, label='Amplitude', lw=1, color="dodgerblue")
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


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    time = 5                # 計測時間[s]
    samplerate = 44100      # サンプリングレート[sampling data count/s)]
    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定

    # フレームサイズ[sampling data count/frame]
    if platform.machine() == "armv7l":  # ARM32bit向け(Raspi等)
        fs = 512
    elif platform.machine() == "x86_64":  # Intel/AMD64bit向け
        fs = 1024
    else:
        fs = 1024
    print("\nFrameSize[sampling data count/frame] = ", fs, "\n")
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === マイク音声レコーディング実行 ===
    data, t = record(index, mic_mode, samplerate, fs, time)
    # index : 使用するマイクのdevice index
    # mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]
    # time : 録音時間[s]

    # === レコーディング音声のwavファイル保存 ===
    now = datetime.datetime.now()

    dirname = 'wav/'
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    filename = dirname + 'recorded-sound_' + \
        now.strftime('%Y%m%d_%H%M%S') + '.wav'
    sf.write(filename, data, samplerate)

    # === フーリエ変換実行 ===
    spectrum, amp, phase, freq = calc_fft(data, samplerate, dbref, A)
    # data : 時間領域波形のAmplitude
    # samplerate : サンプリングレート[sampling data count/s)]
    # dbref : デシベル基準値
    # A : 聴感補正(A特性)の有効/無効設定

    # === レコーディング音声の時間領域波形 & 周波数特性 保存 ===
    plot_time_and_freq(
        t,          # time[s]
        data,       # 時間領域波形 Amplitude
        freq,       # Frequency[Hz]
        amp,        # 周波数特性 Amplitude
        dbref,      # デシベル基準値
        A           # 聴感補正(A特性)の有効/無効設定
    )
