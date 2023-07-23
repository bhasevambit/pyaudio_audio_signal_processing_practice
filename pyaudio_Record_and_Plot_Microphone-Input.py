import scipy
import numpy as np

import platform

from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data_fixed_period
from modules.save_audio_to_wav_file import save_audio_to_wav_file
# from modules.gen_freq_domain_data import gen_freq_domain_data
from modules.a_weighting import a_weighting
from modules.plot_time_and_freq import gen_graph_figure
from modules.plot_time_and_freq import plot_time_and_freq_fixed_period


def calc_fft(data, samplerate, dbref, A):
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


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート [sampling data count/s)]
    time_unit = "s"        # 時間軸単位設定 ("s" or "ms")
    time = 5                # 計測時間 [[s] or [ms]]
    view_range = time         # 時間領域波形グラフ X軸表示レンジ [[s] or [ms]]
    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定

    # フレームサイズ[sampling data count/frame]
    if platform.machine() == "armv7l":  # ARM32bit向け(Raspi等)
        fs = 512
    elif platform.machine() == "x86_64":  # Intel/AMD64bit向け
        fs = 1024
    else:
        fs = 1024
    print("\nFrameSize[sampling data count/frame] = ", fs, "\n")
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === 時間領域波形と周波数特性向けの2つのグラフ領域を作成
    fig, wave_fig, freq_fig = gen_graph_figure()
    # fig       : リアルタイム更新対象のグラフfigure
    # wave_fig  : リアルタイム更新対象の時間領域波形グラフfigure
    # freq_fig  : リアルタイム更新対象の周波数特性グラフfigure

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(index, mic_mode, samplerate, fs)
    # pa : pyaudioクラスオブジェクト
    # stream : マイク入力音声ストリーム

    # === 時間領域波形データ生成 ===
    data_normalized, t = gen_time_domain_data_fixed_period(
        stream, fs, samplerate, time_unit, time)
    # data_normalized   : 時間領域 波形データ(正規化済)
    # t                 : 時間領域 X軸向けデータ[s]

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

    # === レコーディング音声のwavファイル保存 ===
    save_audio_to_wav_file(samplerate, data_normalized)

    # === フーリエ変換実行 ===
    spectrum, amp_normalized, phase, freq = calc_fft(
        data_normalized, samplerate, dbref, A)
    # spectrum          : 周波数特性データ(複素数データ)
    # amp_normalized    : 周波数特性 振幅データ(正規化済)
    # phase             : 周波数特性 位相データ
    # freq              : 周波数特性 X軸向けデータ
    # spectrum, amp_normalized, phase, freq = gen_freq_domain_data(
    #     data, fs, samplerate, dbref, A
    # )
    # spectrum          : 周波数特性データ(複素数データ)
    # amp_normalized    : 周波数特性 振幅データ(正規化済)
    # phase             : 周波数特性 位相データ
    # freq              : 周波数特性 X軸向けデータ

    # === 時間領域波形 & 周波数特性 グラフ保存 ===
    plot_time_and_freq_fixed_period(
        fig,
        wave_fig,
        freq_fig,
        t,
        data_normalized,
        freq,
        amp_normalized,
        view_range,
        dbref,
        A
    )
