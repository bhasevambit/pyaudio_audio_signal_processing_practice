import librosa
import numpy as np
import scipy

from .audio_signal_processing_advanced import gen_mel_filter_bank
from .audio_signal_processing_basic import db, dft_normalize, liner


def gen_cepstrum_data(discrete_data, samplerate, dbref):
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
    # dt = 1 / samplerate  # サンプリング周期[s]
    # quef_data = np.arange(0, len(discrete_data)) * dt

    # LPL(=Low-Pass-Lifter)適用前後を把握するために独立したリストとして複製
    cepstrum_data_lpl = cepstrum_data.copy()

    # LPL(=Low-Pass-Lifter)のカットオフタイム(ケプストラム離散データindex)の推定
    index_range_low = int(samplerate / 800)  # 基本周波数の推定範囲の上限を800Hzとする
    index_range_high = int(samplerate / 40)  # 基本周波数の推定範囲の下限を40Hzとする

    # 基本周期の点数を求める
    voice_fundamental_freq = np.argmax(
        cepstrum_data_lpl[index_range_low:index_range_high]) + index_range_low

    # カットオフタイム(ケプストラム離散データindex)のセット(=基本周期の半分まで抽出)
    cut_off_index = voice_fundamental_freq // 2
    if cut_off_index < 30:
        cut_off_index = 30
    print("cut_off_index = ", cut_off_index)

    # ケプストラム波形へのLPL(=Low-Pass-Lifter)の適用 (高次ケフレンシー成分の0化)
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
    # cepstrum_data             : ケプストラムデータ(対数値)[dB] 1次元配列
    # cepstrum_data_lpl         : LPL(=Low-Pass-Lifter)適用後
    #                             ケプストラムデータ(対数値)[dB] 1次元配列
    return amp_envelope_normalized, cepstrum_data, cepstrum_data_lpl


def gen_mel_cepstrum_data(discrete_data, samplerate, mel_filter_number, dbref):
    # ==========================================================
    # === メルスケール(メル尺度)スペクトル包絡データ生成関数 ===
    # ==========================================================
    # discrete_data     : 時間領域波形 離散データ 1次元配列
    # samplerate        : サンプリング周波数[Hz]
    # mel_filter_number : メルフィルタバンク フィルタ数
    # dbref             : デシベル基準値

    # メルフィルタバンクの作成
    mel_filter_bank = gen_mel_filter_bank(discrete_data, samplerate, mel_filter_number)
    # mel_filter_bank : メルフィルタバンク伝達関数(周波数特性) 1次元配列

    # 時間領域波形 離散データ 1次元配列のDFT(離散フーリエ変換)を実施
    # (scipy.fft.fft()の出力結果spectrumは複素数)
    spectrum_data = scipy.fft.fft(discrete_data)

    # DFT(離散フーリエ変換)データの正規化を実施
    # (振幅成分の正規化 & 負の周波数領域の除外)
    spectrum_normalized, amp_normalized, phase_normalized = dft_normalize(spectrum_data)

    print("len(mel_filter_bank) = ", len(mel_filter_bank))
    print("len(amp_normalized) = ", len(amp_normalized))

    # メルスケール(メル尺度)スペクトル包絡データ生成
    # (正規化後 DFTデータ振幅成分 1次元配列へのメルフィルタバンク伝達関数を適用する)
    melscale_amp_normalized = np.dot(mel_filter_bank, amp_normalized)
    print("len( np.dot(mel_filter_bank, amp_normalized) ) = ", len(melscale_amp_normalized))

    # メル周波数軸データの作成
    melscale_freq_normalized = librosa.mel_frequencies(
        n_mels=mel_filter_number + 2, fmin=0.0, fmax=samplerate / 2, htk=True
    )
    # n_mels : Number of mel bins
    # htk : If True, use HTK formula to convert Hz to mel. Otherwise (False), use Slaney's Auditory Toolbox.

    # mel_freq_normalizedリストの先頭と末尾を除いた上で、メル周波数軸データとする
    melscale_freq_normalized = melscale_freq_normalized[1:-1]
    print("len(melscale_freq_normalized) = ", len(melscale_freq_normalized))

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        melscale_amp_normalized = db(melscale_amp_normalized, dbref)

    # melscale_amp_normalized    : メルスケール(メル尺度)スペクトル包絡データ振幅成分 1次元配列
    # melscale_freq_normalized   : メル周波数軸データ 1次元配列
    # mel_filter_bank           : メルフィルタバンク伝達関数(周波数特性) 1次元配列
    return melscale_amp_normalized, melscale_freq_normalized, mel_filter_bank
