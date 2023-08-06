import scipy
import numpy as np
from modules.audio_signal_processing_basic import db
from modules.audio_signal_processing_basic import liner


def norm(spectrum, dBref):
    # フーリエ変換の振幅を正規化
    spectrum = liner(spectrum, dBref)                   # 計算のために一度リニア値に戻す
    spectrum = np.abs(spectrum / (len(spectrum) / 2))  # 正規化
    spectrum = db(spectrum, dBref)                    # dB値に戻す
    return spectrum


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

    # スペクトルを対数(dB)に変換
    spectrum_db = db(spectrum_data, dbref)

    # 対数スペクトルをIDFT(逆離散フーリエ変換)を実施し、ケプストラム波形を作成
    # (IFFT結果の実数値のみを抽出)
    cepstrum_db = np.real(scipy.ifft(spectrum_db))

    # ローパスリフターのカットオフ指標
    index = 50

    # ケプストラム波形の高次を0にする（ローパスリフター）
    cepstrum_db[index:len(cepstrum_db) - index] = 0

    # ケプストラム波形を再度フーリエ変換してスペクトル包絡を得る
    cepstrum_db_low = scipy.fft.fft(cepstrum_db)

    # frequency軸を作成
    freq = np.linspace(0, samplerate, len(discrete_data))
    # quefrency軸を作成
    quef = np.arange(0, len(discrete_data)) / samplerate

    # グラフ用に振幅を正規化
    # 音声スペクトルの振幅成分を計算
    spectrum_db_amp = norm(spectrum_db, 2e-5)
    # ローパスリフター後のスペクトル包絡の振幅成分を計算
    cepstrum_db_low_amp = norm(cepstrum_db_low, 2e-5)

    return cepstrum_db, spectrum_db_amp, cepstrum_db_low_amp, freq, quef
