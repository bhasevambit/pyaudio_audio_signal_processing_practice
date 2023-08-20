import matplotlib
import numpy as np
import pysptk
import pyworld
from modules.audio_stream import audio_stream_start, audio_stream_stop
from modules.gen_freq_domain_data import (gen_freq_domain_data,
                                          gen_fundamental_freq_data)
from modules.gen_quef_domain_data import gen_quef_domain_data
from modules.gen_time_domain_data import gen_time_domain_data
from modules.get_mic_index import get_mic_index
from modules.get_std_input import (get_selected_mic_index_by_std_input,
                                   get_selected_mode_by_std_input)
from modules.plot_matplot_graph import (gen_graph_figure_for_cepstrum,
                                        plot_time_freq_quef,
                                        plot_time_freq_quef_for_mel)
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
    print("  [ Please INPUT MODE type ]")
    print("")
    print("  0 : Recording MODE")
    print("  1 : Real-Time MODE")
    print("=================================================================")
    print("")
    selected_mode = get_selected_mode_by_std_input(mode_count=2)
    selected_mode = 0   # 【Debugモード】レコーディングモード固定

    if selected_mode == 0:
        selected_mode_name = "'Recording MODE'"
    else:
        selected_mode_name = "'Real-Time MODE'"
    print("\n - Selected MODE = ", selected_mode_name, " - \n")

    # マイクモード (1:モノラル / 2:ステレオ)
    mic_mode = 1

    # サンプリング周波数[Hz]
    if selected_mode == 0:  # レコーディングモード向け
        samplerate = 44100
    else:                   # リアルタイムモード向け
        samplerate = int(44100 / 4)
    print("\nSampling Frequency[Hz] = ", samplerate)

    # 入力音声ストリームバッファあたりのサンプリングデータ数
    if selected_mode == 0:  # レコーディングモード向け
        frames_per_buffer = 512
    else:                   # リアルタイムモード向け
        frames_per_buffer = 1024 * 8
    print(
        "frames_per_buffer [sampling data count/stream buffer] = ",
        frames_per_buffer,
        "\n"
    )

    # グラフタイプ (0:時間領域波形&周波数特性 / 1:時間領域波形&スペクトログラム)
    graph_type = 0

    # 計測時間[s] / 時間領域波形グラフ X軸表示レンジ[s]
    if selected_mode == 0:  # レコーディングモード向け
        time = 3
        time_range = time
        freq_range = int(44100 / 4) / 2
    else:                   # リアルタイムモード向け
        time = 0  # リアルタイムモードの場合は"0"を設定する
        time_range = ((1 / samplerate) * frames_per_buffer) / 10
        freq_range = samplerate / 2

    # デシベル基準値(最小可聴値 20[μPa]を設定)
    dbref = 2e-5

    # 聴感補正(A特性)の有効(True)/無効(False)設定
    A = False   # ケプストラム導出にあたりA特性補正はOFFとする

    # グラフ保存時のファイル名プレフィックス
    filename_prefix = "time-waveform_and_Mel-Cepstrum_"
    # ------------------

    # === マイクチャンネルを自動取得 ===
    # (標準入力にて選択可能とする)
    print("=================================================================")
    print("  [ Please Select Microphone index ]")
    print("=================================================================")
    print("")
    mic_list = get_mic_index()
    selected_index = get_selected_mic_index_by_std_input(mic_list)
    print("\nUse Microphone Index :", selected_index, "\n")

    # === グラフ領域作成 ===
    # (リアルタイムモード向けグラフ描画のためにMain Codeでの生成が必須)
    fig1, wave_fig1, freq_fig1, f0_fig1, ceps_fig = gen_graph_figure_for_cepstrum()
    # fig       : 生成したmatplotlib figureインスタンス
    # wave_fig  : 時間領域波形向けmatplotlib Axesインスタンス
    # freq_fig  : 周波数特性向けmatplotlib Axesインスタンス
    # f0_fig    : 基本周波数 時系列波形向けmatplotlib Axesインスタンス
    # ceps_fig  : ケプストラム向けmatplotlib Axesインスタンス

    fig2, wave_fig2, freq_fig2, f0_fig2, melceps_fig = gen_graph_figure_for_cepstrum()
    # fig           : 生成したmatplotlib figureインスタンス
    # wave_fig      : 時間領域波形向けmatplotlib Axesインスタンス
    # freq_fig      : 周波数特性向けmatplotlib Axesインスタンス
    # f0_fig        : 基本周波数 時系列波形向けmatplotlib Axesインスタンス
    # melceps_fig   : メルケプストラム向けmatplotlib Axesインスタンス

    # === Microphone入力音声ストリーム生成 ===
    pa, stream = audio_stream_start(
        selected_index, mic_mode, samplerate, frames_per_buffer)
    # pa        : 生成したpyaudio.PyAudioクラスオブジェクト
    #             (pyaudio.PyAudio object)
    # stream    : 生成したpyaudio.PyAudio.Streamオブジェクト
    #             (pyaudio.PyAudio.Stream object)

    # === 時間領域波形 & ケプストラムプロット ===
    # キーボードインタラプトあるまでループ処理継続
    while True:
        try:
            # === 時間領域波形データ生成 ===
            data_normalized, time_normalized = gen_time_domain_data(
                stream, frames_per_buffer, samplerate, time
            )
            # data_normalized : 時間領域波形データ(正規化済)
            # time_normalized : 時間領域波形データ(正規化済)に対応した時間軸データ

            # === 周波数特性データ生成 ===
            spectrum_normalized, amp_normalized, phase_normalized, freq_normalized = gen_freq_domain_data(
                data_normalized, samplerate, dbref, A)
            # spectrum_normalized   : 正規化後 DFTデータ 1次元配列
            # amp_normalized        : 正規化後 DFTデータ振幅成分 1次元配列
            # phase_normalized      : 正規化後 DFTデータ位相成分 1次元配列
            # freq_normalized       : 正規化後 周波数軸データ 1次元配列

            # === 基本周波数 時系列データ生成 ===
            f0, time_f0 = gen_fundamental_freq_data(data_normalized, samplerate)
            # f0        : 基本周波数 時系列データ 1次元配列
            # time_f0   : 基本周波数 時系列データに対応した時間軸データ 1次元配列

            # === ケプストラムデータ生成 ===
            amp_envelope_normalized, cepstrum_data, cepstrum_data_lpl = gen_quef_domain_data(
                data_normalized, samplerate, dbref)
            # amp_envelope_normalized   : 正規化後 スペクトル包絡データ振幅成分 1次元配列
            # cepstrum_data             : ケプストラムデータ(対数値)[dB] 1次元配列
            # cepstrum_data_lpl         : LPL(=Low-Pass-Lifter)適用後
            # ケプストラムデータ(対数値)[dB] 1次元配列

            print("--- For Debug ---")
            print("len(data_normalized) = ", len(data_normalized))
            print("len(freq_normalized) = ", len(freq_normalized))

            # スペクトル包絡の抽出 (pyworld使用)
            sp = pyworld.cheaptrick(x=data_normalized, f0=f0, temporal_positions=time_f0, fs=samplerate)
            # sp : Spectral envelope (パワースペクトル(振幅の2乗値) [ndarray]
            print("type(sp) = ", type(sp))
            print("sp.shape = ", sp.shape)
            print("len(sp) = ", len(sp))

            # spに対応した時間軸データ
            sp_time = np.linspace(0, time_range, len(sp))
            print("sp_time = ", sp_time)
            print("len(sp_time) = ", len(sp_time))

            # spに対応した周波数軸データ
            sp_low, sp_column = sp.shape
            sp_freq = np.linspace(0, samplerate / 2, sp_column)
            print("sp_freq = ", sp_freq)
            print("len(sp_freq) = ", len(sp_freq))

            # メルケプストラムに変換前のスペクトル包絡を可視化
            matplotlib.pyplot.figure()
            matplotlib.pyplot.pcolormesh(
                sp_time,
                sp_freq,
                np.log10(sp).T,
                cmap="jet"
            )
            matplotlib.pyplot.ylim(0, 2000)
            matplotlib.pyplot.yticks(np.arange(0, 2020, 100))
            matplotlib.pyplot.xlabel("Time [s] (data count : 6605)")
            matplotlib.pyplot.ylabel("Frequency [Hz] (data count : 1025)")
            matplotlib.pyplot.title('spectral envelope')

            # 非周期性指標の抽出 (extract aperiodicity)
            ap = pyworld.d4c(x=data_normalized, f0=f0, temporal_positions=time_f0, fs=samplerate)
            # ap : Aperiodicity (envelope, linear magnitude relative to spectral envelope) [ndarray]
            print("type(ap) = ", type(ap))
            print("ap.shape = ", ap.shape)

            # 元の音声のスペクトル包絡の算出
            center_sp = int(len(sp) / 2)  # 定常部分を求める(=観測期間ので真ん中の時間を示す時間軸indexを求める)
            print("center_sp = ", center_sp)

            # === メルケプストラムの算出 (pysptk使用) ===
            mcep = pysptk.sp2mc(powerspec=sp, order=19, alpha=0.42)
            # powerspec : Power spectrum
            # order     : Order of mel-cepstrum
            # alpha     : All-pass constant
            # mcep      : mel-cepstrum (shape : order+1)
            print("mcep = ", mcep)
            print("mcep.shape = ", mcep.shape)
            print("len(mcep) = ", len(mcep))

            # mcepに対応した時間軸データ
            mcep_time = np.linspace(0, time_range, len(mcep))
            print("mcep_time = ", mcep_time)
            print("len(mcep_time) = ", len(mcep_time))

            # mcepに対応したメルケプストラムデータ
            mcep_low, mcep_column = mcep.shape
            mcep_yaxis = np.linspace(0, mcep_column, mcep_column)
            print("mcep_yaxis = ", mcep_yaxis)
            print("len(mcep_yaxis) = ", len(mcep_yaxis))

            # メルケプストラムの可視化
            matplotlib.pyplot.figure()
            matplotlib.pyplot.pcolormesh(
                mcep_time,
                mcep_yaxis,
                mcep.T,
                cmap="jet"
            )
            matplotlib.pyplot.ylim(-0.5, 21)
            matplotlib.pyplot.yticks(np.arange(-1, 21.5, 1))
            matplotlib.pyplot.xlabel("Time [s] (data count : 6605)")
            matplotlib.pyplot.ylabel("Mel Cepstrum (data count : 20)")
            matplotlib.pyplot.title('Mel-cepstrum coefficients')

            center_mcep = int(len(mcep) / 2)  # 定常部分を求める(=観測期間ので真ん中の時間を示す時間軸indexを求める)
            print("center_mcep = ", center_mcep)

            # メルケプストラムからスペクトル包絡に変換
            sp_from_mcep = pysptk.mc2sp(mc=mcep, alpha=0.42, fftlen=1024)
            # mc : Mel-spectrum
            # alpha : All-pass constant
            # fftlen  : FFT length
            # sp_from_mcep : Power spectrum (shape : fftlen//2 + 1)
            print("type(sp_from_mcep) = ", type(sp_from_mcep))
            print("sp_from_mcep.shape = ", sp_from_mcep.shape)

            # sp_from_mcepに対応した時間軸データ
            sp_from_mcep_time = np.linspace(0, time_range, len(sp_from_mcep))
            print("sp_from_mcep_time = ", sp_from_mcep_time)
            print("len(sp_from_mcep_time) = ", len(sp_from_mcep_time))

            # spに対応した周波数軸データ
            sp_from_mcep_low, sp_from_mcep_column = sp_from_mcep.shape
            sp_from_mcep_freq = np.linspace(0, samplerate / 2, sp_from_mcep_column)
            print("sp_from_mcep_freq = ", sp_from_mcep_freq)
            print("len(sp_from_mcep_freq) = ", len(sp_from_mcep_freq))

            # メルケプストラムから導出されたスペクトル包絡を可視化
            matplotlib.pyplot.figure()
            matplotlib.pyplot.pcolormesh(
                sp_from_mcep_time,
                sp_from_mcep_freq,
                np.log10(sp_from_mcep).T,
                cmap="jet"
            )
            matplotlib.pyplot.ylim(0, 2000)
            matplotlib.pyplot.yticks(np.arange(0, 2020, 100))
            matplotlib.pyplot.xlabel("Time [s] (data count : 6605)")
            matplotlib.pyplot.ylabel("Frequency [Hz] (data count : 513)")
            matplotlib.pyplot.title('spectral envelope by Mel-Cepstrum')

            # === グラフ表示 ===
            plot_time_freq_quef(
                fig1,
                wave_fig1,
                freq_fig1,
                f0_fig1,
                ceps_fig,
                data_normalized,
                time_normalized,
                time_range,
                amp_normalized,
                amp_envelope_normalized,
                freq_normalized,
                freq_range,
                f0,
                time_f0,
                cepstrum_data,
                cepstrum_data_lpl,
                dbref,
                A,
                selected_mode
            )

            plot_time_freq_quef_for_mel(
                fig2,
                wave_fig2,
                freq_fig2,
                f0_fig2,
                melceps_fig,
                data_normalized,
                time_normalized,
                time_range,
                f0,
                time_f0,
                mcep[center_sp],
                np.log10(sp[center_sp]),
                np.log10(sp_from_mcep[center_sp]),
                dbref,
                A,
                selected_mode
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
