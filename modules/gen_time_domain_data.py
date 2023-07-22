import numpy as np


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
