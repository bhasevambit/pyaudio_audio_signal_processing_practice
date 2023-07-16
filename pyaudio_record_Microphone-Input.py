import pyaudio
import numpy as np
from matplotlib import pyplot as plt
import math


def get_mic_index():
    pa = pyaudio.PyAudio()
    mic_list = []

    print("\n=== Audio Input Devices (Microphone) ===\n")

    for host_index in range(0, pa.get_host_api_count()):  # Host APIで大分類

        host_api_info = pa.get_host_api_info_by_index(host_index)
        print(
            "--- Host API :",
            host_api_info["name"],
            "[INDEX:",
            host_api_info["index"],
            ", Default-device-index:",
            host_api_info["defaultOutputDevice"],
            "] ---"
        )

        for device_index in range(
                0, pa.get_host_api_info_by_index(host_index)['deviceCount']
        ):  # Deviceで小分類

            dev_info = pa.get_device_info_by_host_api_device_index(
                host_index,
                device_index
            )

            if dev_info["maxInputChannels"] != 0:
                print(
                    "index:",
                    dev_info["index"],
                    " ",
                    dev_info["name"],
                    "( IN-Ch:",
                    dev_info["maxInputChannels"],
                    "/ OUT-Ch:",
                    dev_info["maxOutputChannels"],
                    ")"
                )
                mic_list.append(
                    pa.get_device_info_by_index(device_index)['index'])

        print("")

    print("")

    return mic_list


def record(index, mic_mode, samplerate, fs, time):
    ''' 録音する関数 '''

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
        channels=mic_mode,
        rate=samplerate,
        input=True,
        input_device_index=index,
        frames_per_buffer=fs
    )

    # フレームサイズ毎に音声を録音していくループ
    print("\nRecording START")

    for i in range(int(((time / dt) / fs))):

        # print("Recorded sampling data count :", i * fs)
        print("Erapsed Time[s]: ", math.floor(i * fs / samplerate * 100) / 100)

        frame = stream.read(fs)
        data.append(frame)

    print("Recording STOP\n")

    # ストリームの終了
    stream.stop_stream()

    stream.close()
    pa.terminate()

    # データをまとめる処理
    data = b"".join(data)

    # データをNumpy配列に変換/時間軸を作成
    data = np.frombuffer(data, dtype="int16") / \
        float((np.power(2, 16) / 2) - 1)
    t = np.arange(0, fs * (i + 1) * (1 / samplerate), 1 / samplerate)

    return data, t


def plot(t, x, label, xlabel, ylabel, figsize, xlim, ylim, xlog, ylog):
    ''' 汎用プロット関数(1プロット重ね書き) '''

    # フォントの種類とサイズを設定する。
    plt.rcParams['font.size'] = 14
    plt.rcParams['font.family'] = 'Times New Roman'

    # 目盛を内側にする。
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # Subplot設定とグラフの上下左右に目盛線を付ける。
    fig = plt.figure(figsize=figsize)
    ax1 = fig.add_subplot(111)
    ax1.yaxis.set_ticks_position('both')
    ax1.xaxis.set_ticks_position('both')

    # 軸のラベルを設定する。
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)

    # スケールを設定する。
    if xlim != [0, 0]:
        ax1.set_xlim(xlim[0], xlim[1])
    if ylim != [0, 0]:
        ax1.set_ylim(ylim[0], ylim[1])

    # 対数スケール
    if xlog == 1:
        ax1.set_xscale('log')
    if ylog == 1:
        ax1.set_yscale('log')

    # プロットを行う。
    for i in range(len(x)):
        ax1.plot(t[i], x[i], label=label[i], lw=1)
    ax1.legend()

    # レイアウト設定
    fig.tight_layout()

    # グラフを表示する。
    plt.show()
    plt.close()

    return


if __name__ == '__main__':

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    time = 5                # 計測時間[s]
    samplerate = 44100      # サンプリングレート[sampling data count/s)]
    fs = 1024               # フレームサイズ[sampling data count/frame]
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === 録音する関数を実行 ===
    data, t = record(index, mic_mode, samplerate, fs, time)
    # index : 使用するマイクのdevice index
    # mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]
    # time : 録音時間[s]

    # === 波形確認 ===
    plot(
        [t],            # t
        [data],         # x
        ['recorded'],   # label
        'Time [s]',     # xlabel
        'Amplitude',    # ylable
        (8, 4),         # figsize
        [0, 0],         # xlim
        [0, 0],         # ylim
        0,              # xlog
        0               # ylog
    )
