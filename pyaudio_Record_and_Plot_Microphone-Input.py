import platform

from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data
from modules.gen_freq_domain_data import gen_freq_domain_data
from modules.plot_matplot_graph import gen_graph_figure
from modules.plot_matplot_graph import plot_time_and_freq
from modules.save_audio_to_wav_file import save_audio_to_wav_file
from modules.save_matplot_graph import save_matplot_graph


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート [sampling data count/s)]
    time = 5                # 計測時間 [[s] or [ms]] (リアルタイムモードの場合は"0"を設定)
    view_range = time       # 時間領域波形グラフ X軸表示レンジ [[s] or [ms]]
    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定
    plot_pause = -1         # グラフ表示のpause時間 [s] (非リアルタイムモード(指定時間録音)の場合は"-1"を設定)
    filename_prefix = "time-waveform_and_freq-response_"    # グラフ保存時のファイル名プレフィックス

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
    fig, wave_fig, freq_fig = gen_graph_figure()
    # fig       : 生成したmatplotlib figureインスタンス
    # wave_fig  : 時間領域波形向けmatplotlib Axesインスタンス
    # freq_fig  : 周波数特性向けmatplotlib Axesインスタンス

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(
        index, mic_mode, samplerate, frames_per_buffer)
    # pa        : 生成したpyaudio.PyAudioクラスオブジェクト
    #             (pyaudio.PyAudio object)
    # stream    : 生成したpyaudio.PyAudio.Streamオブジェクト
    #             (pyaudio.PyAudio.Stream object)

    # === 時間領域波形データ生成 ===
    data_normalized, time_normalized = gen_time_domain_data(
        stream, frames_per_buffer, samplerate, time
    )
    # data_normalized : 時間領域波形データ(正規化済)
    # time_normalized : 時間領域波形データ(正規化済)に対応した時間軸データ

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

    # === レコーディング音声のwavファイル保存 ===
    save_audio_to_wav_file(samplerate, data_normalized)

    # === 周波数特性データ生成 ===
    spectrum_normalized, amp_normalized, phase_normalized, freq_normalized = gen_freq_domain_data(
        data_normalized, samplerate, dbref, A)
    # spectrum_normalized   : 正規化後 DFTデータ 1次元配列
    # amp_normalized        : 正規化後 DFTデータ振幅成分 1次元配列
    # phase_normalized      : 正規化後 DFTデータ位相成分 1次元配列
    # freq_normalized       : 正規化後 周波数軸データ 1次元配列

    # === 時間領域波形 & 周波数特性 グラフ表示 ===
    plot_time_and_freq(
        fig,
        wave_fig,
        freq_fig,
        data_normalized,
        time_normalized,
        amp_normalized,
        freq_normalized,
        view_range,
        dbref,
        A,
        plot_pause
    )

    # === 時間領域波形 & 周波数特性 グラフ保存 ===
    save_matplot_graph(filename_prefix)
