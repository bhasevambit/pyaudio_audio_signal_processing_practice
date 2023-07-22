import numpy as np
import math

from modules.audio_stream import audio_stream_stop


def audio_recode(samplerate, fs, pa, stream, time):
    # ============================================
    # === Microphone入力音声レコーディング関数 ===
    # ============================================
    # samplerate    : サンプリングレート[sampling data count/s)]
    # fs            : フレームサイズ[sampling data count/frame]
    # pa            : pyaudioクラスオブジェクト
    # stream        : マイク入力音声ストリーム
    # time          : 録音時間[s]

    # フレームサイズ毎に音声を録音していくループ
    print("Recording START")
    data = []
    dt = 1 / samplerate
    i = 0

    for i in range(int(((time / dt) / fs))):
        erapsed_time = math.floor(((i * fs) / samplerate) * 100) / 100
        print("  - Erapsed Time[s]: ", erapsed_time)

        frame = stream.read(fs)
        data.append(frame)

    print("Recording STOP\n")

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

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
