import scipy
import numpy as np
from modules.audio_signal_processing_basic import db
from modules.audio_signal_processing_basic import a_weighting


def gen_freq_domain_data(data_normalized, samplerate, dbref, A):
    # ================================
    # === 周波数特性データ生成関数 ===
    # ================================
    # data_normalized   : 時間領域 波形データ(正規化済)
    # samplerate        : サンプリングレート [sampling data count/s)]
    # dbref             : デシベル基準値
    # A                 : 聴感補正(A特性)の有効(True)/無効(False)設定

    # 信号のフーリエ変換
    spectrum = scipy.fft.fft(data_normalized)

    # 振幅成分算出
    amp = np.abs(spectrum)

    # 位相成分算出 & 位相をラジアンから度に変換
    phase_rad = np.angle(spectrum)
    phase = np.degrees(phase_rad)

    # 振幅成分の正規化
    # 離散フーリエ変換の定義から、求まる振幅ampを入力データの振幅に合わせるため 1/N 倍して振幅を計算する。
    # 加えて、フーリエ変換された N 個のスペクトル（振幅やパワー） は、サンプリング周波数の 1/2
    # の周波数（ナイキスト周波数）を堺に左右対称となる事から、スペクトルの値は対になる対称成分を足し合わせたものが、
    # 入力データの実データと一致するため、スペクトル値をさらに2倍する正規化を施す
    amp_normalized_pre = (amp / len(data_normalized)) * 2

    # amp_normalized_preは、負の周波数領域データも含むため、
    # 「要素数(len(amp_normalized_pre) / 2」までの要素をスライス抽出
    amp_normalized = amp_normalized_pre[1:int(len(amp_normalized_pre) / 2)]

    # 周波数軸を作成
    dt = 1 / samplerate  # サンプリング周期[s]
    freq_bipolar = scipy.fft.fftfreq(len(spectrum), d=dt)

    # freq_bipolarは、負の周波数領域軸データも含むため、
    # 「要素数(len(freq_bipolar) / 2」までの要素をスライス抽出
    freq = freq_bipolar[1:int(len(freq_bipolar) / 2)]

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        amp_normalized = db(amp_normalized, dbref)

        # dB変換されていてAがTrueの時に聴感補正する
        if A:
            amp_normalized += a_weighting(freq)

    return spectrum, amp_normalized, phase, freq


def get_freq_domain_data_of_signal_spctrgrm(
    data_normalized, samplerate, frames_per_buffer, overlap_rate, dbref, A
):
    # =============================================================
    # === 周波数特性データ生成関数 (scipy.signal.spectrogram版) ===
    # =============================================================
    # data_normalized       : 時間領域 波形データ(正規化済)
    # samplerate            : サンプリングレート [sampling data count/s)]
    # frames_per_buffer     : 入力音声ストリームバッファあたりのサンプリングデータ数
    # overlap_rate          : オーバーラップ率 [%]
    # dbref                 : デシベル基準値
    # A                     : 聴感補正(A特性)の有効(True)/無効(False)設定

    freq_spctrgrm, time_spctrgrm, spectrogram = scipy.signal.spectrogram(
        data_normalized,
        fs=samplerate,
        window="hann",  # 窓関数はHanning窓を使用
        nperseg=1024,
        # noverlapはオーバラップするサンプリングデータ数
        noverlap=(frames_per_buffer * (overlap_rate / 100)),
        nfft=2047,
        # scalingは"spectrum"を指定する事でスペクトログラムデータ単位が「振幅の2乗」となるパワースペクトルとなる
        scaling="spectrum",
        # modeを"magnitude"とすることで、スペクトログラムデータとして振幅が算出される
        mode="magnitude"
    )

    print("freq_spctrgrm.shape = ", freq_spctrgrm.shape)
    print("time_spctrgrm.shape = ", time_spctrgrm.shape)
    print("spectrogram.shape [scipy org] = ", spectrogram.shape)

    # 聴感補正曲線を計算
    a_scale = a_weighting(freq_spctrgrm)
    print("a_scale.shape = ", a_scale.shape)

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        spectrogram = db(spectrogram, dbref)
        print("spectrogram.shape [dB] = ", spectrogram.shape)

        # A=Trueの場合に、A特性補正を行う
        if A:
            for i in range(len(time_spctrgrm)):
                # 各時間軸データ(freq_spctrgrmと同じ次元サイズ)に対して、A特性補正を実施
                spectrogram[:, i] += a_scale

            print("spectrogram.shape [dB(A)]= ", spectrogram.shape)

    return freq_spctrgrm, time_spctrgrm, spectrogram


def gen_freq_domain_data_of_stft(
    time_array_after_window,
    samplerate,
    frames_per_buffer,
    N_ave,
    acf,
    dbref,
    A
):
    # ===============================================================
    # === 周波数特性データ生成関数 (Full Scratch STFT Function版) ===
    # ===============================================================
    # time_array_after_window   : 時間領域 波形データ(正規化/オーバーラップ処理/hanning窓関数適用済)
    # samplerate                : サンプリングレート [sampling data count/s)]
    # frames_per_buffer         : 入力音声ストリームバッファあたりのサンプリングデータ数
    # N_ave                     : オーバーラップ処理における切り出しフレーム数
    # acf                       : 振幅補正係数(Amplitude Correction Factor)
    # dbref                     : デシベル基準値
    # A                         : 聴感補正(A特性)の有効(True)/無効(False)設定

    print("N_ave = ", N_ave)

    # 平均化FFTする関数
    fft_array = []

    # 周波数軸を作成
    freq_spctrgrm = np.linspace(0, samplerate, frames_per_buffer)
    print("freq_spctrgrm.shape = ", freq_spctrgrm.shape)

    # 聴感補正曲線を計算
    a_scale = a_weighting(freq_spctrgrm)
    print("a_scale.shape = ", a_scale.shape)

    # FFT実施後に、配列にdBで追加し、窓関数補正値をかけ、(frames_per_buffer/2)の正規化を実施
    for i in range(N_ave):

        # dbrefが0以上の場合は、dB変換し、配列に追加する
        if dbref > 0:
            # (frames_per_buffer/2)の正規化、および窓関数補正値(acf)を乗算を実施
            fft_array.append(
                db(
                    acf *
                    np.abs(scipy.fft.fft(time_array_after_window[i]) /
                           (frames_per_buffer / 2)),
                    dbref
                )
            )

        else:
            # (frames_per_buffer/2)の正規化、および窓関数補正値(acf)を乗算を実施
            fft_array.append(
                acf *
                np.abs(scipy.fft.fft(time_array_after_window[i]) /
                       (frames_per_buffer / 2))
            )

    # numpy.ndarray変換を行う
    fft_array = np.array(fft_array)
    print("fft_array.shape = ", fft_array.shape)

    # dbrefが0以上、かつ、A=Trueの場合に、A特性補正を行う
    if (dbref > 0) and A:
        fft_array = fft_array + a_scale
        print("fft_array.shape [dB(A)] = ", fft_array.shape)

    # 全てのFFT波形の平均を計算
    fft_mean = np.mean(
        np.sqrt(
            fft_array ** 2),
        axis=0)

    return fft_array, fft_mean, freq_spctrgrm
