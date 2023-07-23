import platform

from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data
from modules.gen_freq_domain_data import gen_freq_domain_data
from modules.plot_matplot_graph import gen_graph_figure
from modules.plot_matplot_graph import plot_time_and_freq


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Sound Parameters ---
    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    samplerate = 44100      # サンプリングレート [sampling data count/s)]
    time_unit = "ms"        # 時間軸単位設定 ("s" or "ms")
    time = 0                # 計測時間 [[s] or [ms]] (リアルタイムモードの場合は"0"を設定)
    view_range = 50         # 時間領域波形グラフ X軸表示レンジ [[s] or [ms]]
    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定
    plot_pause = 0.0001     # グラフ表示のpause時間 [s] (非リアルタイムモード(指定時間録音)の場合は"-1"を設定)

    # 入力音声ストリームバッファあたりのサンプリングデータ数
    if platform.machine() == "armv7l":  # ARM32bit向け(Raspi等)
        frames_per_buffer = 512
    elif platform.machine() == "x86_64":  # Intel64bit向け
        # 16384以下の場合、「OSError: [Errno -9981] Input
        # overflowed」が発生したため、16384としている
        frames_per_buffer = 32768
    elif platform.machine() == "AMD64":  # AMD64bit向け
        # グラフが正常表示されなかったため、16384としている
        frames_per_buffer = 16384
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
    # fig       : matplotlib グラフfigure
    # wave_fig  : matplotlib 時間領域波形グラフfigure
    # freq_fig  : matplotlib 周波数特性グラフfigure

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(
        index, mic_mode, samplerate, frames_per_buffer)
    # pa        : pyaudioクラスオブジェクト
    # stream    : マイク入力音声ストリーム

    # === 時間領域波形 & 周波数特性リアルタイムプロット ===
    # キーボードインタラプトあるまでループ処理継続
    while True:
        try:
            # === 時間領域波形データ生成 ===
            data_normalized, t = gen_time_domain_data(
                stream, frames_per_buffer, samplerate, time_unit, time)
            # data_normalized   : 時間領域 波形データ(正規化済)
            # t                 : 時間領域 X軸向けデータ[ms]

            # === 周波数特性データ生成 ===
            spectrum, amp_normalized, phase, freq = gen_freq_domain_data(
                data_normalized, samplerate, dbref, A
            )
            # spectrum          : 周波数特性データ(複素数データ)
            # amp_normalized    : 周波数特性 振幅データ(正規化済)
            # phase             : 周波数特性 位相データ
            # freq              : 周波数特性 X軸向けデータ

            # === 時間領域波形 & 周波数特性 グラフ表示 ===
            plot_time_and_freq(
                fig,
                wave_fig,
                freq_fig,
                data_normalized,
                t,
                amp_normalized,
                freq,
                view_range,
                dbref,
                A,
                plot_pause
            )

        except KeyboardInterrupt:   # Ctrl+c で終了
            break

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

    print("=================")
    print("= Main Code END =")
    print("=================\n")
