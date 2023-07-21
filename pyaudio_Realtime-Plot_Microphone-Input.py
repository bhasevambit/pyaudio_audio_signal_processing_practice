import pyaudio
import numpy as np
from matplotlib import pyplot as plt
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


def gen_time_domain_data(stream, fs):
    # ==================================
    # === 時間領域波形データ生成関数 ===
    # ==================================
    # stream : マイク入力音声データストリーム
    # fs : フレームサイズ[sampling data count/frame]
    audio_data = stream.read(fs)
    data = np.frombuffer(audio_data, dtype='int16')

    return data


def gen_freq_domain_data(data, fs, samplerate):
    # ================================
    # === 周波数特性データ生成関数 ===
    # ================================
    # data : 時間領域波形データ
    # fs : フレームサイズ[sampling data count/frame]
    # samplerate : サンプリングレート[sampling data count/s)]

    # 周波数特性データ算出
    fft_data = np.fft.fft(data)

    # 周波数データを取得
    sampling_period = 1 / samplerate
    freq = np.fft.fftfreq(fs, d=sampling_period)

    return fft_data, freq


def plot_waveform_and_freq_response(
        data_buffer,
        data,
        fft_data,
        fs,
        plot_pause,
        view_range
):
    # =======================================================
    # === Microphone入力音声ストリームデータ プロット関数 ===
    # =======================================================
    # data_buffer : データバッファ
    # data : 時間領域波形データ
    # fft_data : 周波数特性データ
    # fs : フレームサイズ[sampling data count/frame]
    # plot_pause : グラフリアルタイム表示のポーズタイム[s]
    # view_range : 時間領域波形グラフ X軸表示レンジ[sample count]

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
    fft_fig.set_ylabel('Amplitude')

    # スケール設定
    wave_fig.set_xlim(len(data_buffer) - view_range, len(data_buffer))
    wave_fig.set_ylim(-1, 1)
    fft_fig.set_xlim(0, 5000)

    # レイアウト設定
    fig.tight_layout()

    # ストリームデータの正規化
    # dataについては、16bit量子化であり、かつ正負符号を持つ事から、
    # ±32767(=±((2^16 / 2) - 1))の範囲にデータが入る事から、dataを((2^16 / 2) - 1)で割る事で、正規化している
    data_normalized = np.frombuffer(data, dtype="int16") / \
        float((np.power(2, 16) / 2) - 1)

    data_buffer = np.append(data_buffer[fs:], data_normalized)

    # 時間領域波形グラフプロット
    wave_fig.plot(data_buffer, color='blue')

    # 周波数特性グラフプロット
    fft_fig.plot(
        freq[:fs // 20],
        np.abs(fft_data[:fs // 20]),
        color='dodgerblue'
    )

    plt.pause(plot_pause)

    fft_fig.cla()
    wave_fig.cla()


def audio_stop(pa, stream):
    # ============================================
    # === Microphone入力音声ストリーム停止関数 ===
    # ============================================
    stream.stop_stream()
    stream.close()
    pa.terminate()


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート[sampling data count/s)]
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
    (pa, stream) = audio_start(index, mic_mode, samplerate, fs)
    # index : 使用するマイクのdevice index
    # mic_mode : mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]

    # === 波形プロット用のバッファ生成 ===
    data_buffer = np.zeros(fs * 16, int)    # データバッファ

    # === 時間領域波形と周波数特性向けの2つのグラフ領域を作成
    fig = plt.figure()
    wave_fig = fig.add_subplot(2, 1, 1)
    fft_fig = fig.add_subplot(2, 1, 2)

    # === 時間領域波形 & 周波数特性リアルタイムプロット ===
    # キーボードインタラプトあるまでループ処理継続
    while True:
        try:
            # === 時間領域波形データ生成 ===
            data = gen_time_domain_data(stream, fs)
            # === 周波数特性データ生成 ===
            fft_data, freq = gen_freq_domain_data(data, fs, samplerate)

            # === グラフプロット ===
            plot_waveform_and_freq_response(
                data_buffer, data, fft_data, fs, plot_pause, view_range)

        except KeyboardInterrupt:   # Ctrl+c で終了
            break

    # Microphone入力音声ストリーム停止
    audio_stop(pa, stream)

    print("=================")
    print("= Main Code END =")
    print("=================\n")
