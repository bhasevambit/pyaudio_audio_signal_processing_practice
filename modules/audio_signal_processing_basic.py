import scipy
import numpy as np


def db(x, dbref):
    # ==============================
    # === 音圧レベル[dB]演算関数 ===
    # ==============================
    # x     : 観測値[pa]
    # dbref : 基準値[pa]

    # dbref[pa]を基準としたx[pa]の音圧レベル[dB]の算出
    with np.errstate(divide='ignore'):
        y = 20 * np.log10(x / dbref)

    return y


def dft_normalize(discrete_data, spectrum_data, samplerate):
    # ===============================================
    # === DFT(離散フーリエ変換)データの正規化関数 ===
    # ===============================================
    # discrete_data : 離散データ1次元配列 (DFT元データ)
    # spectrum_data : DFTデータ1次元配列
    # samplerate    : 離散データ生成時のサンプリング周波数[Hz]

    # 振幅成分算出
    amp = np.abs(spectrum_data)

    # 位相成分算出 & 位相をラジアンから度に変換
    phase_rad = np.angle(spectrum_data)
    phase = np.degrees(phase_rad)

    # === 振幅成分の正規化 ===
    # 離散フーリエ変換の定義から、求まる振幅ampを入力データの振幅に合わせるため 1/N 倍して振幅を計算する。
    # 加えて、フーリエ変換された N 個のスペクトル（振幅やパワー） は、サンプリング周波数の 1/2
    # の周波数（ナイキスト周波数）を堺に左右対称となる事から、スペクトルの値は対になる対称成分を足し合わせたものが、
    # 入力データの実データと一致するため、スペクトル値をさらに2倍する正規化を施す
    amp_normalized_pre = (amp / len(discrete_data)) * 2

    # amp_normalized_preは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(amp_normalized_pre) / 2」までの要素)
    amp_normalized = amp_normalized_pre[:int(len(amp_normalized_pre) / 2)]
    print("amp_normalized = ", amp_normalized)
    print("len(amp_normalized) = ", len(amp_normalized))

    # === 位相成分の正規化 ===
    # phaseは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(phase) / 2」までの要素)
    phase_normalized = phase[:int(len(phase) / 2)]
    print("phase_normalized = ", phase_normalized)
    print("len(phase_normalized) = ", len(phase_normalized))

    # === 正規化済データと連動した周波数軸の作成 ===
    dt = 1 / samplerate  # サンプリング周期[s]
    freq_bipolar = scipy.fft.fftfreq(len(spectrum_data), d=dt)

    # freq_bipolarは、負の周波数領域軸データも含むため、
    # 「要素数(len(freq_bipolar) / 2」までの要素をスライス抽出
    freq_data = freq_bipolar[:int(len(freq_bipolar) / 2)]
    print("freq_data = ", freq_data)
    print("len(freq_data) = ", len(freq_data))

    return amp_normalized, phase_normalized, freq_data


def a_weighting(f):
    # ==================================
    # === 聴感補正関数 (A特性カーブ) ===
    # ==================================
    # f : 周波数特性 周波数軸データ

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
