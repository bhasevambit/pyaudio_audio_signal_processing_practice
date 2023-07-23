import scipy
import numpy as np
from modules.a_weighting import a_weighting


def gen_freq_domain_data(data_normalized, fs, samplerate, dbref, A):
    # ================================
    # === 周波数特性データ生成関数 ===
    # ================================
    # data_normalized   : 時間領域 波形データ(正規化済)
    # fs                : フレームサイズ [sampling data count/frame]
    # samplerate        : サンプリングレート [sampling data count/s)]
    # dbref             : デシベル基準値
    # A                 : 聴感補正(A特性)の有効(True)/無効(False)設定

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
    phase_rad = np.angle(spectrum)
    phase = np.degrees(phase_rad)

    # 正規化した振幅成分をFFTデータとする
    # amp_normalizedは、負の周波数領域データも含むため、「フレームサイズ/2」までの要素をスライス抽出
    amp_normalized = amp_normalized[1:int(fs / 2)]

    # 周波数軸を作成
    # freq_bipolarは、負の周波数領域軸データも含むため、「フレームサイズ/2」までの要素をスライス抽出
    dt = 1 / samplerate  # サンプリング周期[s]
    freq_bipolar = scipy.fft.fftfreq(fs, d=dt)
    freq = freq_bipolar[1:int(fs / 2)]

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        with np.errstate(divide='ignore'):
            amp_normalized = 20 * np.log10(amp_normalized / dbref)

        # dB変換されていてAがTrueの時に聴感補正する
        if A:
            amp_normalized += a_weighting(freq)

    return spectrum, amp_normalized, phase, freq


def gen_freq_domain_data_fixed_period(data, samplerate, dbref, A):
    # ============================================
    # === フーリエ変換関数 (dB変換とA補正付き) ===
    # ============================================

    # 信号のフーリエ変換
    print("Fourier transform START")
    spectrum = scipy.fft.fft(data)

    # 振幅成分算出
    amp = np.sqrt((spectrum.real ** 2) + (spectrum.imag ** 2))
    print("  - Amplitude Caluculation END")

    # 振幅成分の正規化
    amp_normalized = amp / (len(data) / 2)
    print("  - Amplitude Normalization END")

    # 位相成分算出 & 位相をラジアンから度に変換
    phase = np.arctan2(spectrum.imag, spectrum.real)
    phase = np.degrees(phase)
    print("  - Phase Caluculation END")

    # 周波数軸を作成
    freq = np.linspace(0, samplerate, len(data))
    print("  - Frequency Axis generation END")

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        amp_normalized = 20 * np.log10(amp_normalized / dbref)

        # dB変換されていてAがTrueの時に聴感補正する
        if A:
            amp_normalized += a_weighting(freq)

    print("Fourier transform END\n")
    return spectrum, amp_normalized, phase, freq
