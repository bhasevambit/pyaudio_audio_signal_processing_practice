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


def dft_normalize(discrete_data, spectrum_data):
    # ===============================================
    # === DFT(離散フーリエ変換)データの正規化関数 ===
    # ===============================================
    # discrete_data : 離散データ 1次元配列 (DFT元データ)
    # spectrum_data : DFTデータ 1次元配列

    # === DFTデータの正規化 ===
    # spectrum_dataは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(spectrum_data) / 2」までの要素)
    spectrum_normalized = spectrum_data[:int(len(spectrum_data) / 2)]

    # === 振幅成分の正規化 ===
    # 振幅成分算出
    amp = np.abs(spectrum_data)

    # 離散フーリエ変換の定義から、求まる振幅ampを入力データの振幅に合わせるため 1/N 倍して振幅を計算する。
    # 加えて、フーリエ変換された N 個のスペクトル（振幅やパワー） は、サンプリング周波数の 1/2
    # の周波数（ナイキスト周波数）を堺に左右対称となる事から、スペクトルの値は対になる対称成分を足し合わせたものが、
    # 入力データの実データと一致するため、スペクトル値をさらに2倍する正規化を施す
    amp_normalized_pre = (amp / len(discrete_data)) * 2

    # amp_normalized_preは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(amp_normalized_pre) / 2」までの要素)
    amp_normalized = amp_normalized_pre[:int(len(amp_normalized_pre) / 2)]

    # === 位相成分の正規化 ===
    # 位相成分算出 & 位相をラジアンから度に変換
    phase_rad = np.angle(spectrum_data)
    phase = np.degrees(phase_rad)

    # phaseは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(phase) / 2」までの要素)
    phase_normalized = phase[:int(len(phase) / 2)]

    return spectrum_normalized, amp_normalized, phase_normalized


def dft_freq_normalize(freq_data):
    # ========================================================
    # === DFT(離散フーリエ変換) 周波数軸データの正規化関数 ===
    # ========================================================
    # freq_data     : DFTデータに対応した周波数軸データ 1次元配列

    # === 正規化済データと連動した周波数軸の作成 ===
    # freq_dataは、負の周波数領域軸データも含むため、
    # 「要素数(len(freq_data) / 2」までの要素をスライス抽出
    freq_normalized = freq_data[:int(len(freq_data) / 2)]

    return freq_normalized


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
