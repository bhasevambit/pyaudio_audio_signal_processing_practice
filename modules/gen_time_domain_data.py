import numpy as np
import math


def normalize_time_domain_data(audio_data, dtype):
    # ====================================
    # === 時間領域波形データ正規化関数 ===
    # ====================================
    # audio_data    : 時間領域波形データ
    # dtype         : 変換する1次元配列の型

    # 時間領域波形データを dtype引数で指定された整数型 1次元配列に変換
    data = np.frombuffer(audio_data, dtype)

    # 時間領域波形データの正規化
    # dataについては、16bit量子化であり、かつ正負符号を持つ事から、
    # ±32767(=±((2^16 / 2) - 1))の範囲にデータが入る事から、dataを((2^16 / 2) - 1)で割る事で、正規化している
    data_normalized = data / float((np.power(2, 16) / 2) - 1)

    return data_normalized


def gen_time_domain_x_axis_data(samplerate, data_normalized, time_unit):
    # ====================================
    # === 時間領域 X軸データ生成関数 ===
    # ====================================
    # samplerate        : サンプリングレート[sampling data count/s)]
    # data_normalized   : 時間領域 波形データ(正規化済)
    # time_unit         : 時間軸単位

    dt = 1 / samplerate
    t = np.arange(0, len(data_normalized) * dt, dt)

    if time_unit == "ms":
        t = t * 1000    # msに単位変換

    return t


def gen_time_domain_data_realtime(stream, fs, samplerate):
    # ==================================================
    # === 時間領域波形データ生成関数(リアルタイム版) ===
    # ==================================================
    # stream     : マイク入力音声データストリーム
    # fs         : フレームサイズ [sampling data count/frame]
    # samplerate : サンプリングレート [sampling data count/s)]

    # 時間領域波形データの生成
    audio_data = stream.read(fs)

    # 時間領域波形データの正規化
    data_normalized = normalize_time_domain_data(audio_data, "int16")

    # 時間領域 X軸データの生成
    t = gen_time_domain_x_axis_data(samplerate, data_normalized, "ms")

    return data_normalized, t


def gen_time_domain_data_fixed_period(stream, fs, samplerate, time):
    # ==============================================
    # === 時間領域波形データ生成関数(時間指定版) ===
    # ==============================================
    # stream     : マイク入力音声データストリーム
    # fs         : フレームサイズ [sampling data count/frame]
    # samplerate : サンプリングレート [sampling data count/s)]
    # time       : 録音時間[s]

    # フレームサイズ毎にマイク入力音声ストリームデータ生成
    audio_data_united = []
    dt = 1 / samplerate
    i = 0

    print("Audio Stream Recording START")

    for i in range(int(((time / dt) / fs))):
        erapsed_time = math.floor(((i * fs) / samplerate) * 100) / 100
        print("  - Erapsed Time[s]: ", erapsed_time)

        audio_data_fs = stream.read(fs)
        audio_data_united.append(audio_data_fs)

    print("Audio Stream Recording END\n")

    # フレームサイズ毎音声ストリームデータを連結
    # frame毎に、要素が分かれていたdataを、要素間でbyte列連結
    audio_data = b"".join(audio_data_united)

    # 時間領域波形データの正規化
    data_normalized = normalize_time_domain_data(audio_data, "int16")

    # 時間領域 X軸データの生成
    t = gen_time_domain_x_axis_data(samplerate, data_normalized, "s")

    return data_normalized, t
