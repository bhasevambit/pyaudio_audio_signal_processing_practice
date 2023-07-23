import scipy
import numpy as np
from modules.a_weighting import a_weighting


def gen_freq_domain_data(data_normalized, samplerate, dbref, A):
    # ================================
    # === 周波数特性データ生成関数 ===
    # ================================
    # data_normalized   : 時間領域 波形データ(正規化済)
    # samplerate        : サンプリングレート [sampling data count/s)]
    # dbref             : デシベル基準値
    # A                 : 聴感補正(A特性)の有効(True)/無効(False)設定

    # 信号のフーリエ変換
    spectrum = scipy.fft.fft(data_normalized)

    # 振幅成分算出
    amp = np.abs(spectrum)

    # 位相成分算出 & 位相をラジアンから度に変換
    phase_rad = np.angle(spectrum)
    phase = np.degrees(phase_rad)

    # 振幅成分の正規化
    # 離散フーリエ変換の定義から、求まる振幅ampを入力データの振幅に合わせるため 1/N 倍して振幅を計算する。
    # 加えて、フーリエ変換された N 個のスペクトル（振幅やパワー） は、サンプリング周波数の 1/2
    # の周波数（ナイキスト周波数）を堺に左右対称となる事から、スペクトルの値は対になる対称成分を足し合わせたものが、
    # 入力データの実データと一致するため、スペクトル値をさらに2倍する正規化を施す
    amp_normalized_pre = (amp / len(data_normalized)) * 2

    # amp_normalized_preは、負の周波数領域データも含むため、
    # 「要素数(len(amp_normalized_pre) / 2」までの要素をスライス抽出
    amp_normalized = amp_normalized_pre[1:int(len(amp_normalized_pre) / 2)]

    # 周波数軸を作成
    dt = 1 / samplerate  # サンプリング周期[s]
    freq_bipolar = scipy.fft.fftfreq(len(spectrum), d=dt)

    # freq_bipolarは、負の周波数領域軸データも含むため、
    # 「要素数(len(freq_bipolar) / 2」までの要素をスライス抽出
    freq = freq_bipolar[1:int(len(freq_bipolar) / 2)]

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        with np.errstate(divide='ignore'):
            amp_normalized = 20 * np.log10(amp_normalized / dbref)

        # dB変換されていてAがTrueの時に聴感補正する
        if A:
            amp_normalized += a_weighting(freq)

    return spectrum, amp_normalized, phase, freq
