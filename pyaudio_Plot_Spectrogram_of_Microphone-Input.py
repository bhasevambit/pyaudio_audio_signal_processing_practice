import scipy

import platform

from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data
from modules.plot_matplot_graph import gen_graph_figure
from modules.plot_matplot_graph import plot_time_and_spectrogram
from modules.save_audio_to_wav_file import save_audio_to_wav_file
from modules.save_matplot_graph import save_matplot_graph


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート [sampling data count/s)]
    time_unit = "s"         # 時間軸単位設定 ("s" or "ms")
    time = 5                # 計測時間 [[s] or [ms]] (リアルタイムモードの場合は"0"を設定)
    view_range = time       # 時間領域波形グラフ X軸表示レンジ [[s] or [ms]]
    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定
    plot_pause = -1         # グラフ表示のpause時間 [s] (非リアルタイムモード(指定時間録音)の場合は"-1"を設定)

    # スペクトログラムデータ算出モード (0:scipy.signal.spectrogram()関数を使用 / 1:自作STFT関数を使用)
    spctrgrm_mode = 0

    # 入力音声ストリームバッファあたりのサンプリングデータ数
    if platform.machine() == "armv7l":  # ARM32bit向け(Raspi等)
        frames_per_buffer = 512
    elif platform.machine() == "x86_64":  # Intel/AMD64bit向け
        frames_per_buffer = 1024
    else:
        frames_per_buffer = 1024
    print(
        "\nframes_per_buffer [sampling data count/stream buffer] = ",
        frames_per_buffer,
        "\n"
    )
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === 時間領域波形と周波数特性向けの2つのグラフ領域を作成
    fig, wave_fig, spctrgrm_fig = gen_graph_figure()
    # fig           : matplotlib グラフfigure
    # wave_fig      : matplotlib 時間領域波形グラフfigure
    # spctrgrm_fig  : matplotlib スペクトログラムグラフfigure

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(
        index, mic_mode, samplerate, frames_per_buffer)
    # pa : pyaudioクラスオブジェクト
    # stream : マイク入力音声ストリーム

    # === 時間領域波形データ生成 ===
    data_normalized, t = gen_time_domain_data(
        stream, frames_per_buffer, samplerate, time_unit, time)
    # data_normalized   : 時間領域 波形データ(正規化済)
    # t                 : 時間領域 X軸向けデータ[s]

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

    # === レコーディング音声のwavファイル保存 ===
    save_audio_to_wav_file(samplerate, data_normalized)

    # === スペクトログラムデータ算出実行 ===
    if spctrgrm_mode == 0:
        # scipy.signal.spectrogram()を使用する場合
        freq_spctrgrm, time_spctrgrm, spectrogram = scipy.signal.spectrogram(
            data_normalized,
            fs=samplerate
        )
        # freq_spctrgrm          : Array of sample frequencies
        # time_spctrgrm          : Array of segment times
        # spectrogram            : Spectrogram

    else:
        # 自作STFT関数を使用する場合
        pass

    # === 時間領域波形 & スペクトログラム グラフ表示 ===
    plot_time_and_spectrogram(
        fig,
        wave_fig,
        spctrgrm_fig,
        data_normalized,
        t,
        view_range,
        freq_spctrgrm,
        time_spctrgrm,
        spectrogram
    )

    # === 時間領域波形 & スペクトログラム グラフ保存 ===
    save_matplot_graph()
