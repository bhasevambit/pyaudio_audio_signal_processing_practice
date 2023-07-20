import pyaudio
import numpy as np
from matplotlib import pyplot as plt
import math
import platform


def get_mic_index():
    # ================================
    # === Microphone Index取得関数 ===
    # ================================
    pa = pyaudio.PyAudio()
    mic_list = []

    print("=== Audio Input Devices (Microphone) ===\n")

    for host_index in range(0, pa.get_host_api_count()):  # Host APIで大分類

        host_api_info = pa.get_host_api_info_by_index(host_index)
        print(
            "  --- Host API :",
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
                    "  index:",
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

    return mic_list


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

    for i in range(int(((time / dt) / fs))):

        # print("Recorded sampling data count :", i * fs)
        print(
            "  - Erapsed Time[s]: ",
            math.floor(
                i *
                fs /
                samplerate *
                100) /
            100)

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
    data = np.frombuffer(data, dtype="int16") / \
        float((np.power(2, 16) / 2) - 1)
    t = np.arange(0, fs * (i + 1) * (1 / samplerate), 1 / samplerate)

    return data, t


def audio_start(index, mic_mode, samplerate, fs):
    # ============================================
    # === Microphone入力音声ストリーム生成関数 ===
    # ============================================
    # index : 使用するマイクのdevice index
    # mic_mode : mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]

    pa = pyaudio.PyAudio()

    # ストリームの開始
    stream = pa.open(
        format=pyaudio.paInt16,
        # pyaudio.paInt16 = 16bit量子化モード (音声時間領域波形の振幅を-32767～+32767に量子化)
        channels=mic_mode,
        rate=samplerate,
        input=True,
        input_device_index=index,
        frames_per_buffer=fs
    )

    return pa, stream


def audio_stop(pa, stream):
    # ============================================
    # === Microphone入力音声ストリーム停止関数 ===
    # ============================================
    stream.stop_stream()
    stream.close()
    pa.terminate()


def read_plot_data(stream, fs):
    # =======================================================
    # === Microphone入力音声ストリームデータ プロット関数 ===
    # =======================================================
    # fs : フレームサイズ[sampling data count/frame]

    data = stream.read(fs)
    audio_data = np.frombuffer(data, dtype='int16')

    plt.plot(audio_data)
    plt.draw()
    plt.pause(0.001)
    plt.cla()


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート[sampling data count/s)]

    if platform.machine() == "armv7l":  # Raspi等、ARM32bit版の場合は、フレームサイズを512とする(overflow対策)
        fs = 512                # フレームサイズ[sampling data count/frame]
    else:
        fs = 1024               # フレームサイズ[sampling data count/frame]
    print("\nFrameSize[sampling data count/frame] = ", fs, "\n")
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === Microphone入力音声ストリーム生成 ===
    (audio, stream) = audio_start(index, mic_mode, samplerate, fs)
    # index : 使用するマイクのdevice index
    # mic_mode : mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]

    # === Microphone入力音声ストリーム リアルタイムプロット ===
    # キーボードインタラプトあるまでループ処理継続
    while True:
        try:
            read_plot_data(stream, fs)
        except KeyboardInterrupt:
            break

    # Microphone入力音声ストリーム停止
    audio_stop(audio, stream)
