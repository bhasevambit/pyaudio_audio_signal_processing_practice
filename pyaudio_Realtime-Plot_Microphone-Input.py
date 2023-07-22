from matplotlib import pyplot as plt

import platform

from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data
from modules.gen_freq_domain_data import gen_freq_domain_data
from modules.plot_waveform_and_freq_response import plot_waveform_and_freq_response

if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート[sampling data count/s)]
    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定
    plot_pause = 0.0001     # グラフリアルタイム表示のポーズタイム[s]
    view_range = 50         # 時間領域波形グラフ X軸表示レンジ[ms]

    # フレームサイズ[sampling data count/frame]
    if platform.machine() == "armv7l":  # ARM32bit向け(Raspi等)
        fs = 512
    elif platform.machine() == "x86_64":  # Intel64bit向け
        # 4096以下の場合、「OSError: [Errno -9981] Input overflowed」が発生したため、16384としている
        fs = 16384
    elif platform.machine() == "AMD64":  # AMD64bit向け
        # グラフが正常表示されなかったため、16384としている
        fs = 16384
    else:
        fs = 1024
    print("\nFrameSize[sampling data count/frame] = ", fs, "\n")
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(index, mic_mode, samplerate, fs)
    # pa : pyaudioクラスオブジェクト
    # stream : マイク入力音声ストリーム

    # === 時間領域波形と周波数特性向けの2つのグラフ領域を作成
    fig = plt.figure()
    wave_fig = fig.add_subplot(2, 1, 1)
    freq_fig = fig.add_subplot(2, 1, 2)

    # === 時間領域波形 & 周波数特性リアルタイムプロット ===
    # キーボードインタラプトあるまでループ処理継続
    while True:
        try:
            # === 時間領域波形データ生成 ===
            data_normalized, t = gen_time_domain_data(stream, fs, samplerate)
            # data_normalized   : 時間領域 波形データ(正規化済)
            # t                 : 時間領域 X軸向けデータ[ms]

            # === 周波数特性データ生成 ===
            spectrum, amp_normalized, phase, freq = gen_freq_domain_data(
                data_normalized, fs, samplerate, dbref, A
            )
            # spectrum          : 周波数特性データ(複素数データ)
            # amp_normalized    : 周波数特性 振幅データ(正規化済)
            # phase             : 周波数特性 位相データ
            # freq              : 周波数特性 X軸向けデータ

            # === グラフプロット ===
            plot_waveform_and_freq_response(
                fig,
                wave_fig,
                freq_fig,
                data_normalized,
                t,
                amp_normalized,
                freq,
                plot_pause,
                view_range,
                dbref,
                A)

        except KeyboardInterrupt:   # Ctrl+c で終了
            break

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

    print("=================")
    print("= Main Code END =")
    print("=================\n")
