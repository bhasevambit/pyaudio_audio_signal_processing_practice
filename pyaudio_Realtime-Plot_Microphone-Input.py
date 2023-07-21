import pyaudio
import scipy
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

    # ストリームデータの正規化
    # dataについては、16bit量子化であり、かつ正負符号を持つ事から、
    # ±32767(=±((2^16 / 2) - 1))の範囲にデータが入る事から、dataを((2^16 / 2) - 1)で割る事で、正規化している
    data_normalized = np.frombuffer(data, dtype="int16") / \
        float((np.power(2, 16) / 2) - 1)

    return data_normalized


def gen_freq_domain_data(data_normalized, fs, samplerate, dbref, A):
    # ================================
    # === 周波数特性データ生成関数 ===
    # ================================
    # data_normalized : 時間領域波形データ(正規化済)
    # fs : フレームサイズ[sampling data count/frame]
    # samplerate : サンプリングレート[sampling data count/s)]
    # dbref : デシベル基準値
    # A : 聴感補正(A特性)の有効(True)/無効(False)設定

    # 信号のフーリエ変換
    spectrum = scipy.fft.fft(data_normalized)

    # 振幅成分算出
    amp = np.abs(spectrum)

    # 振幅成分の正規化
    amp_normalized = (amp / len(data_normalized)) * 2
    # 離散フーリエ変換の定義から、求まる振幅ampを入力データの振幅に合わせるため 1/N 倍して振幅を計算する。
    # 加えて、フーリエ変換された N 個のスペクトル（振幅やパワー） は、サンプリング周波数の 1/2
    # の周波数（ナイキスト周波数）を堺に左右対称となる事から、スペクトルの値は対になる対称成分を足し合わせたものが、
    # 入力データの実データと一致するため、スペクトル値をさらに2倍する正規化を施す

    # 位相成分算出 & 位相をラジアンから度に変換
    # phase_rad = np.angle(spectrum)
    # phase = np.degrees(phase_rad)

    # 正規化した振幅成分をFFTデータとする
    # amp_normalizedは、負の周波数領域データも含むため、「フレームサイズ/2」までの要素をスライス抽出
    fft_data = amp_normalized[1:int(fs / 2)]

    # 周波数軸を作成
    # freq_bipolarは、負の周波数領域軸データも含むため、「フレームサイズ/2」までの要素をスライス抽出
    dt = 1 / samplerate  # サンプリング周期[s]
    freq_bipolar = scipy.fft.fftfreq(fs, d=dt)
    freq = freq_bipolar[1:int(fs / 2)]

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        fft_data = 20 * np.log10(fft_data / dbref)

        # dB変換されていてAがTrueの時に聴感補正する
        if A:
            fft_data += aweightings(freq)

    return fft_data, freq


def aweightings(f):
    # ==================================
    # === 聴感補正関数 (A特性カーブ) ===
    # ==================================

    if f[0] == 0:
        f[0] = 1e-6
    else:
        pass

    ra = (np.power(12194, 2) * np.power(f, 4)) / \
         ((np.power(f, 2) + np.power(20.6, 2)) *
          np.sqrt((np.power(f, 2) + np.power(107.7, 2)) *
                  (np.power(f, 2) + np.power(737.9, 2))) *
          (np.power(f, 2) + np.power(12194, 2)))

    a = 20 * np.log10(ra) + 2.00

    return a


def plot_waveform_and_freq_response(
        data_normalized,
        fft_data,
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
    # fft_data : 周波数特性データ
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
    fft_fig.set_xlim(0, 5000)
    fft_fig.set_ylim(-10, 80)

    # レイアウト設定
    fig.tight_layout()

    # 時間領域波形グラフプロット
    wave_fig.plot(data_normalized, color="blue")

    # 周波数特性グラフプロット
    fft_fig.plot(freq, fft_data, color="dodgerblue")

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
    pa, stream = audio_start(index, mic_mode, samplerate, fs)
    # index : 使用するマイクのdevice index
    # mic_mode : mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]

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

            # === 周波数特性データ生成 ===
            fft_data, freq = gen_freq_domain_data(
                data_normalized, fs, samplerate, dbref, A
            )

            # === グラフプロット ===
            plot_waveform_and_freq_response(
                data_normalized,
                fft_data,
                freq,
                fs,
                plot_pause,
                view_range,
                dbref,
                A)

        except KeyboardInterrupt:   # Ctrl+c で終了
            break

    # Microphone入力音声ストリーム停止
    audio_stop(pa, stream)

    print("=================")
    print("= Main Code END =")
    print("=================\n")
