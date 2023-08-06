import scipy
import numpy as np
from modules.audio_signal_processing_basic import db
from modules.audio_signal_processing_basic import liner
from modules.audio_signal_processing_basic import dft_normalize


def gen_quef_domain_data(discrete_data, samplerate, dbref):
    # ==================================
    # === ケプストラムデータ生成関数 ===
    # ==================================
    # discrete_data     : 時間領域波形 離散データ 1次元配列
    # samplerate        : サンプリング周波数[Hz]
    # dbref             : デシベル基準値

    # 時間領域波形 離散データ 1次元配列のDFT(離散フーリエ変換)を実施
    # (scipy.fft.fft()の出力結果spectrumは複素数)
    spectrum_data = scipy.fft.fft(discrete_data)

    # DFTデータ(複素数)を対数[dB](dbref基準)に変換
    spectrum_data_log = db(spectrum_data, dbref)

    # 対数DFTデータ(複素数対数)に対して、IDFT(逆離散フーリエ変換)を実施
    spectrum_idft = scipy.ifft(spectrum_data_log)

    # IDFTデータの実数値を抽出し、ケプストラム波形データを作成
    cepstrum_data = np.real(spectrum_idft)

    # ケプストラム波形データに対応したケフレンシー軸データを作成
    # (時間領域波形 離散データ 1次元配列の要素数を最大値とした１次元配列の各要素にサンプリング周期[s]を乗算)
    dt = 1 / samplerate  # サンプリング周期[s]
    quef_data = np.arange(0, len(discrete_data)) * dt

    # LPL(=Low-Pass-Lifter)のカットオフタイム(ケプストラム離散データindex)を設定
    cut_off_index = 50

    # ケプストラム波形へのLPL(=Low-Pass-Lifter)の適用 (高次ケフレンシー成分の0化)
    cepstrum_data_lpl = cepstrum_data
    cepstrum_data_lpl[cut_off_index:len(cepstrum_data_lpl) - cut_off_index] = 0

    # ケプストラム波形データ 1次元配列のDFT(離散フーリエ変換)を実施し、
    # スペクトル包絡データ(=対数DFTデータ(複素数対数))を生成
    spectrum_envelope_log = scipy.fft.fft(cepstrum_data_lpl)

    # 正規化のために、複素数対数を複素数リニア値に変換
    spectrum_envelope_data = liner(spectrum_envelope_log, dbref)

    # スペクトル包絡データ(=DFT(離散フーリエ変換)データ)の正規化を実施
    # (振幅成分の正規化 & 負の周波数領域の除外)
    spectrum_envelope_normalized, amp_envelope_normalized, phase_envelope_normalized = dft_normalize(
        spectrum_envelope_data)

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        amp_envelope_normalized = db(amp_envelope_normalized, dbref)

    # amp_envelope_normalized   : 正規化後 スペクトル包絡データ振幅成分 1次元配列
    # cepstrum_data             : ケプストラムデータ[dB]
    # quef_data                 : ケプストラムデータに対応したケフレンシー軸データ 1次元配列
    return amp_envelope_normalized, cepstrum_data, quef_data
