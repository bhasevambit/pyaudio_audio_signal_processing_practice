import numpy as np


def gen_time_domain_data(stream, fs, samplerate):
    # ==================================
    # === 時間領域波形データ生成関数 ===
    # ==================================
    # stream     : マイク入力音声データストリーム
    # fs         : フレームサイズ [sampling data count/frame]
    # samplerate : サンプリングレート [sampling data count/s)]

    # 時間領域波形データの生成
    audio_data = stream.read(fs)
    data = np.frombuffer(audio_data, dtype='int16')

    # 時間領域波形データの正規化
    # dataについては、16bit量子化であり、かつ正負符号を持つ事から、
    # ±32767(=±((2^16 / 2) - 1))の範囲にデータが入る事から、dataを((2^16 / 2) - 1)で割る事で、正規化している
    data_normalized = data / float((np.power(2, 16) / 2) - 1)

    # 時間領域 X軸データの生成
    dt = 1 / samplerate
    t = np.arange(0, len(data_normalized) * dt, dt)
    t = t * 1000    # msに単位変換

    return data_normalized, t
