from modules.get_std_input import get_selected_mode_by_std_input
from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data
from modules.gen_freq_domain_data import gen_freq_domain_data_of_signal_spctrgrm
from modules.gen_freq_domain_data import gen_freq_domain_data_of_stft
from modules.audio_signal_processing_advanced import overlap
from modules.audio_signal_processing_advanced import window
from modules.plot_matplot_graph import gen_graph_figure
from modules.plot_matplot_graph import gen_graph_figure_for_realtime_spctrgrm
from modules.plot_matplot_graph import plot_time_and_spectrogram
from modules.save_audio_to_wav_file import save_audio_to_wav_file
from modules.save_matplot_graph import save_matplot_graph


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Parameters ---
    # 動作モード (0:レコーディングモード / 1:リアルタイムモード)
    # (標準入力にて変更可能とする)
    print("")
    print("=================================================================")
    print("  [ Please INPUT MODE type ] (1/2)")
    print("")
    print("  0 : Recording MODE")
    print("  1 : Real-Time MODE")
    print("=================================================================")
    print("")
    selected_mode = get_selected_mode_by_std_input(mode_count=2)

    if selected_mode == 0:
        selected_mode_name = "'Recording MODE'"
    else:
        selected_mode_name = "'Real-Time MODE'"
    print("\n - Selected MODE = ", selected_mode_name, " - \n")

    # スペクトログラムデータ算出モード (0:scipy.signal.spectrogram()関数を使用 / 1:自作STFT関数を使用)
    # (標準入力にて変更可能とする)
    print("")
    print("=================================================================")
    print("  [ Please INPUT Spectrogram Mode ] (2/2)")
    print("")
    print("  0 : Use scipy.signal.spectrogram Function")
    print("  1 : Use Full Scratch STFT Function")
    print("=================================================================")
    print("")
    spctrgrm_mode = get_selected_mode_by_std_input(mode_count=2)

    if spctrgrm_mode == 0:
        spctrgrm_mode_name = "'scipy.signal.spectrogram Function Mode'"
    else:
        spctrgrm_mode_name = "'Full Scratch STFT Function Mode'"
    print("\n - Selected Spectrogram Mode = ", spctrgrm_mode_name, " - \n")

    # マイクモード (1:モノラル / 2:ステレオ)
    mic_mode = 1

    # サンプリング周波数 [sampling data count/s]
    samplerate = 44100

    # 入力音声ストリームバッファあたりのサンプリングデータ数
    if selected_mode == 0:
        frames_per_buffer = 512
    else:
        # 8192以下ではリアルタイムでのグラフ描画が不可であったため"16384"とした
        frames_per_buffer = 16384
    print(
        "\nframes_per_buffer [sampling data count/stream buffer] = ",
        frames_per_buffer,
        "\n"
    )

    # グラフタイプ (0:時間領域波形&周波数特性 / 1:時間領域波形&スペクトログラム)
    graph_type = 1

    # 計測時間[s] / 時間領域波形グラフ X軸表示レンジ[s]
    if selected_mode == 0:
        time = 5
        view_range = time
    else:
        # リアルタイムモードの場合は"0"を設定する
        time = 0
        view_range = 0.050  # リアルタイムモードの場合は"50[ms]"を設定

    # デシベル基準値(最小可聴値 20[μPa]を設定)
    dbref = 2e-5

    # 聴感補正(A特性)の有効(True)/無効(False)設定
    A = True

    # STFT(短時間フーリエ変換)を行う時系列データ数(=STFTフレーム長)
    stft_frame_size = 1536
    # オーバーラップ率 [%]
    overlap_rate = 20
    # 使用する窓関数 ("hann" : Hanning窓)
    window_func = "hann"

    # グラフ保存時のファイル名プレフィックス
    filename_prefix = "time-waveform_and_spectrogram_"
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

    # === グラフ領域作成 ===
    # (リアルタイムモード向けグラフ描画のためにMain Codeでの生成が必須)
    if selected_mode == 0:
        # === レコーディングモードの場合 ===
        fig, wave_fig, spctrgrm_fig = gen_graph_figure(graph_type)
        # fig           : 生成したmatplotlib figureインスタンス
        # wave_fig      : 時間領域波形向けmatplotlib Axesインスタンス
        # spctrgrm_fig  : スペクトログラム向けmatplotlib Axesインスタンス
    else:
        # === リアルタイムモードの場合 ===
        fig, spctrgrm_fig = gen_graph_figure_for_realtime_spctrgrm()
        wave_fig = 0    # 未使用変数の初期化
        # fig           : 生成したmatplotlib figureインスタンス
        # spctrgrm_fig  : スペクトログラム向けmatplotlib Axesインスタンス

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(
        index, mic_mode, samplerate, frames_per_buffer)
    # pa        : 生成したpyaudio.PyAudioクラスオブジェクト
    #             (pyaudio.PyAudio object)
    # stream    : 生成したpyaudio.PyAudio.Streamオブジェクト
    #             (pyaudio.PyAudio.Stream object)

    # === 時間領域波形 & 周波数特性リアルタイムプロット ===
    # キーボードインタラプトあるまでループ処理継続
    while True:
        try:
            # === 時間領域波形データ生成 ===
            data_normalized, time_normalized = gen_time_domain_data(
                stream, frames_per_buffer, samplerate, time
            )
            # data_normalized : 時間領域波形データ(正規化済)
            # time_normalized : 時間領域波形データ(正規化済)に対応した時間軸データ

            # === スペクトログラムデータ算出 ===
            if spctrgrm_mode == 0:

                # ================================================
                # === scipy.signal.spectrogram()を使用する場合 ===
                # ================================================

                freq_spctrgrm, time_spctrgrm, spectrogram = gen_freq_domain_data_of_signal_spctrgrm(
                    data_normalized, samplerate, stft_frame_size, overlap_rate, window_func, dbref, A)
                # freq_spctrgrm         : スペクトログラム y軸向けデータ[Hz]
                # time_spctrgrm         : スペクトログラム x軸向けデータ[s]
                # spectrogram           : スペクトログラム 振幅データ

            else:

                # ==================================
                # === 自作STFT関数を使用する場合 ===
                # ==================================

                # オーバーラップ処理の実行
                data_overlaped, N_ave, final_time = overlap(
                    data_normalized, samplerate, stft_frame_size, overlap_rate
                )
                # data_overlaped    : オーバーラップ抽出された時間領域波形配列(正規化済)
                # N_ave             : オーバーラップ処理における切り出しフレーム数
                # final_time        : オーバーラップ処理で切り出したデータの最終時刻[s]

                # 窓関数の適用
                data_applied_window, acf = window(
                    data_overlaped, stft_frame_size, N_ave, window_func
                )
                # data_applied_window   : 時間領域 波形データ(正規化/オーバーラップ処理/hanning窓関数適用済)
                # acf                   : 振幅補正係数(Amplitude Correction Factor)

                # STFT(Short-Time Fourier Transform)の実行
                freq_spctrgrm, time_spctrgrm, spectrogram = gen_freq_domain_data_of_stft(
                    data_applied_window, samplerate, stft_frame_size, N_ave, final_time, acf, dbref, A)
                # freq_spctrgrm         : スペクトログラム y軸向けデータ[Hz]
                # time_spctrgrm         : スペクトログラム x軸向けデータ[s]
                # spectrogram           : スペクトログラム 振幅データ

            # === グラフ表示 ===
            plot_time_and_spectrogram(
                fig,
                wave_fig,
                spctrgrm_fig,
                data_normalized,
                time_normalized,
                view_range,
                freq_spctrgrm,
                time_spctrgrm,
                spectrogram,
                dbref,
                A,
                selected_mode,
                spctrgrm_mode
            )

            if selected_mode == 0:
                # レコーディングモードの場合、While処理を1回で抜ける
                break

        except KeyboardInterrupt:
            # 「ctrl+c」が押下された場合、While処理を抜ける
            break

    if selected_mode == 0:
        # レコーディングモードの場合、音声およびグラフを保存する

        # === レコーディング音声のwavファイル保存 ===
        save_audio_to_wav_file(samplerate, data_normalized)

        # === グラフ保存 ===
        save_matplot_graph(filename_prefix)

    # === Microphone入力音声ストリーム停止 ===
    audio_stream_stop(pa, stream)

    print("=================")
    print("= Main Code END =")
    print("=================\n")
