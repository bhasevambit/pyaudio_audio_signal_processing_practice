import numpy as np


def db(x, dbref):
    # ================================
    # === 音圧レベル dB値 算出関数 ===
    # ================================
    # x     : 観測値[pa]
    # dbref : 基準値[pa]

    # dbref[pa]を基準としたx[pa]の音圧レベル[dB]の算出
    with np.errstate(divide='ignore'):
        y = 20 * np.log10(x / dbref)

    # y : 音圧レベル変換値[dB]
    return y


def liner(x, dbref):
    # ====================================
    # === 音圧レベル リニア値 算出関数 ===
    # ====================================
    # x     : 観測値[dB]
    # dbref : 基準値[pa]

    # dbref[pa]を基準としたx[dB]の音圧レベル[pa]の算出
    with np.errstate(divide='ignore'):
        y = dbref * 10 ** (x / 20)

    # y : 音圧レベル変換値[pa]
    return y


def discrete_data_normalize(discrete_data, dtype):
    # ====================================================
    # === 量子化により生成された離散データの正規化関数 ===
    # ====================================================
    # discrete_data     : 量子化により生成された離散データ 1次元配列
    # dtype             : 変換する1次元配列の型 (例："int16")

    # 離散データ 1次元配列を、dtype引数で指定された整数型のnumpy.ndarrayに変換
    discrete_data_ndarray = np.frombuffer(discrete_data, dtype)

    # === 離散データの正規化 ===
    # discrete_data_ndarrayは、振幅成分が16bit量子化されたデータであり、かつ正負符号を持ち、
    # ±32767(=±((2^16 / 2) - 1))の範囲にデータが入る事から、
    # dataを((2^16 / 2) - 1)で除算する事で、振幅成分を"-1.0～+1.0"の範囲に正規化する
    data_normalized = discrete_data_ndarray / float((np.power(2, 16) / 2) - 1)

    # data_normalized : 正規化済 離散データ 1次元配列
    return data_normalized


def gen_time_axis_data(discrete_data, samplerate):
    # ========================================================
    # === 時間領域波形データに対応した時間軸データ生成関数 ===
    # ========================================================
    # discrete_data     : 時間領域波形 離散データ 1次元配列
    # samplerate        : サンプリング周波数[sampling data count/s)]

    # サンプリング周期[s]を算出
    dt = 1 / samplerate

    # 時間領域波形データに対応した時間軸データ 1次元配列の生成
    time_axis_data = np.arange(0, len(discrete_data) * dt, dt)

    # time_axis_data : 時間領域波形データに対応した時間軸データ 1次元配列
    return time_axis_data


def dft_normalize(spectrum_data):
    # ===============================================
    # === DFT(離散フーリエ変換)データの正規化関数 ===
    # ===============================================
    # spectrum_data : DFTデータ 1次元配列

    # === DFTデータの正規化(負の周波数領域の除外) ===
    # spectrum_dataは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(spectrum_data) / 2」までの要素)
    spectrum_normalized = spectrum_data[:int(len(spectrum_data) / 2)]

    # === 振幅成分の正規化(スペクトル正規化 & 負の周波数領域の除外) ===
    # 振幅成分算出
    amp = np.abs(spectrum_data)

    # 離散フーリエ変換の定義から、求まる振幅ampを入力データの振幅に合わせるため 1/N 倍して振幅を計算する。
    # 加えて、フーリエ変換された N 個のスペクトル(振幅やパワー)は、サンプリング周波数の 1/2
    # の周波数（ナイキスト周波数）を堺に左右対称となる事から、スペクトルの値は対になる対称成分を足し合わせたものが、
    # 入力データの実データと一致するため、スペクトル値をさらに2倍する正規化を施す
    amp_normalized_pre = (amp / len(spectrum_data)) * 2

    # amp_normalized_preは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(amp_normalized_pre) / 2」までの要素)
    amp_normalized = amp_normalized_pre[:int(len(amp_normalized_pre) / 2)]

    # === 位相成分の正規化(負の周波数領域の除外) ===
    # 位相成分算出 & 位相をラジアンから度に変換
    phase_rad = np.angle(spectrum_data)
    phase = np.degrees(phase_rad)

    # phaseは、負の周波数領域データも含むため、
    # 正の周波数領域データをスライス抽出 (開始要素から「要素数(len(phase) / 2」までの要素)
    phase_normalized = phase[:int(len(phase) / 2)]

    # spectrum_normalized   : 正規化後 DFTデータ 1次元配列
    # amp_normalized        : 正規化後 DFTデータ振幅成分 1次元配列
    # phase_normalized      : 正規化後 DFTデータ位相成分 1次元配列
    return spectrum_normalized, amp_normalized, phase_normalized


def dft_negative_freq_domain_exlusion(freq_domain_data):
    # ======================================
    # === 負の周波数領域データの除外関数 ===
    # ======================================
    # freq_domain_data     : 負の周波数領域を含む離散データ 1次元配列

    # freq_domain_dataは、負の周波数領域軸データも含むため、
    # 「要素数(len(freq_domain_data) / 2」までの要素をスライス抽出
    freq_domain_data_normalized = freq_domain_data[:int(
        len(freq_domain_data) / 2)]

    # freq_domain_data_normalized   : 正の周波数領域のみの離散データ 1次元配列
    return freq_domain_data_normalized


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

    # a : 聴感補正 振幅データ[dB] 1次元配列
    return a


def gen_melfreq_axis_data(f):
    # ==================================
    # === 聴感補正関数 (A特性カーブ) ===
    # ==================================
    # f : 周波数特性 周波数軸データ

    # 周波数からメル周波数への変換式： メル周波数[mel] = 2595 * log10(1 + 周波数[Hz] / 700)
    # 正規化後 周波数軸データ 1次元配列(freq_normalized)をメル周波数軸データ 1次元配列に変換する
    melfreq_data = 2595 * np.log10(1 + f / 700)

    # melfreq_data : メル周波数軸データ 1次元配列
    return melfreq_data
