from modules.get_std_input import get_selected_mode_by_std_input
from modules.get_mic_index import get_mic_index
from modules.audio_stream import audio_stream_start
from modules.audio_stream import audio_stream_stop
from modules.gen_time_domain_data import gen_time_domain_data
from modules.gen_freq_domain_data import get_freq_domain_data_of_signal_spctrgrm
from modules.gen_freq_domain_data import gen_freq_domain_data_of_stft
from modules.audio_signal_processing_advanced import overlap
from modules.audio_signal_processing_advanced import hanning
from modules.plot_matplot_graph import plot_time_and_spectrogram
from modules.save_audio_to_wav_file import save_audio_to_wav_file
from modules.save_matplot_graph import save_matplot_graph


if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # --- Parameters ---
    # スペクトログラムデータ算出モード (0:scipy.signal.spectrogram()関数を使用 / 1:自作STFT関数を使用)
    # (標準入力にて変更可能とする)
    print("")
    print("=================================================================")
    print("  [ Please INPUT Spectrogram Mode ]")
    print("")
    print("  0 : Use scipy.signal.spectrogram Function")
    print("  1 : Use Full Scratch STFT Function")
    print("=================================================================")
    print("")
    spctrgrm_mode = get_selected_mode_by_std_input(mode_count=2)

    if spctrgrm_mode == 0:
        selected_mode = "'scipy.signal.spectrogram Function Mode'"
    else:
        selected_mode = "'Full Scratch STFT Function Mode'"
    print("\n - Selected Spectrogram Mode = ", selected_mode, " - \n")

    # サンプリング周波数 [sampling data count/s]
    samplerate = 44100

    # 入力音声ストリームバッファあたりのサンプリングデータ数
    frames_per_buffer = 512
    print(
        "\nframes_per_buffer [sampling data count/stream buffer] = ",
        frames_per_buffer,
        "\n"
    )

    mic_mode = 1            # マイクモード (1:モノラル / 2:ステレオ)
    time_unit = "s"         # 時間軸単位設定 ("s" or "ms")
    time = 5                # 計測時間 [[s] or [ms]] (リアルタイムモードの場合は"0"を設定)
    view_range = time       # 時間領域波形グラフ X軸表示レンジ [[s] or [ms]]

    dbref = 2e-5            # デシベル基準値(最小可聴値 20[μPa]を設定)
    A = True                # 聴感補正(A特性)の有効(True)/無効(False)設定

    stft_frame_size = 1536  # STFT(短時間フーリエ変換)を行う時系列データ数(=STFTフレーム長)
    overlap_rate = 20       # オーバーラップ率 [%]
    window_func = "hann"    # 使用する窓関数 ("hann" : Hanning窓)

    # グラフ保存時のファイル名プレフィックス
    filename_prefix = "time-waveform_and_spectrogram_"
    # グラフ表示のpause時間 [s] (非リアルタイムモード(指定時間録音)の場合は"-1"を設定)
    plot_pause = -1
    # ------------------------

    # === マイクチャンネルを自動取得 ===
    index = get_mic_index()[0]
    print("Use Microphone Index :", index, "\n")

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

        # ================================================
        # === scipy.signal.spectrogram()を使用する場合 ===
        # ================================================
        freq_spctrgrm, time_spctrgrm, spectrogram = get_freq_domain_data_of_signal_spctrgrm(
            data_normalized, samplerate, stft_frame_size, overlap_rate, window_func, dbref, A)

        # 未使用変数を初期化
        fft_array = []
        final_time = 0

    else:

        # ==================================
        # === 自作STFT関数を使用する場合 ===
        # ==================================

        # オーバーラップ処理の実行
        time_array, N_ave, final_time = overlap(
            data_normalized, samplerate, stft_frame_size, overlap_rate
        )
        # time_array    : オーバーラップ抽出された時間領域波形配列(正規化済)
        # N_ave         : オーバーラップ処理における切り出しフレーム数
        # final_time    : オーバーラップ処理で切り出したデータの最終時刻[s]

        # Hanning窓関数の適用
        time_array_after_window, acf = hanning(
            time_array, stft_frame_size, N_ave
        )
        # time_array_after_window   : 時間領域 波形データ(正規化/オーバーラップ処理/hanning窓関数適用済)
        # acf                       : 振幅補正係数(Amplitude Correction Factor)

        # STFT(Short-Time Fourier Transform)の実行
        freq_spctrgrm, time_spctrgrm, spectrogram = gen_freq_domain_data_of_stft(
            time_array_after_window, samplerate, stft_frame_size, N_ave, final_time, acf, dbref, A)
        # fft_array         : STFT Spectrogramデータ
        # fft_mean          : 全てのFFT波形の平均値
        # freq              : 周波数軸データ

        # スペクトログラムで縦軸周波数、横軸時間にするためにデータを転置
        fft_array = spectrogram.T

    # === 時間領域波形 & スペクトログラム グラフ表示 ===
    plot_time_and_spectrogram(
        data_normalized,
        t,
        view_range,
        freq_spctrgrm,
        time_spctrgrm,
        spectrogram,
        fft_array,
        samplerate,
        final_time,
        dbref,
        A,
        spctrgrm_mode
    )

    # === 時間領域波形 & スペクトログラム グラフ保存 ===
    save_matplot_graph(filename_prefix)
