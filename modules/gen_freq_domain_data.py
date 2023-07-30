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

    # 時間領域 波形データ(正規化済)のフーリエ変換を実施
    # (scipy.fft.fft()の出力結果spectrumは複素数)
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
        data_normalized,
        samplerate,
        stft_frame_size,
        overlap_rate,
        window_func,
        dbref,
        A):
    # =============================================================
    # === 周波数特性データ生成関数 (scipy.signal.spectrogram版) ===
    # =============================================================
    # data_normalized       : 時間領域 波形データ(正規化済)
    # samplerate            : サンプリングレート [sampling data count/s)]
    # stft_frame_size       : STFT(短時間フーリエ変換)を行う時系列データ数(=STFTフレーム長)
    # overlap_rate          : オーバーラップ率 [%]
    # window_func           : 使用する窓関数
    # dbref                 : デシベル基準値
    # A                     : 聴感補正(A特性)の有効(True)/無効(False)設定

    freq_spctrgrm, time_spctrgrm, spectrogram = scipy.signal.spectrogram(
        # xは、「Time series of measurement values」
        # (= スペクトログラムデータの元となる時系列データ配列)
        x=data_normalized,
        # fsは、「Sampling frequency of the x time series」
        # (= サンプリング周波数)
        fs=samplerate,
        # windowは、使用する窓関数
        window=window_func,
        # npersegは、「Length of each segment」
        # (= STFT(短時間フーリエ変換)を行う時系列データ数(=STFTフレーム長))
        nperseg=stft_frame_size,
        # noverlapは、オーバラップするサンプリングデータ数を指定する
        # ([*] noverlapは、nperseg以下である必要あり)
        noverlap=(stft_frame_size * (overlap_rate / 100)),
        # nfftは、短時間FFTにおける周波数軸方向のデータ数を指定する
        # ([*] (設定値+1)/2 がスペクトログラムの周波数軸要素数となる)
        # ([*] nfftは、nperseg以上である必要あり)
        nfft=(stft_frame_size * 2) - 1,
        # scalingを"spectrum"を指定する事でスペクトログラムデータ単位が「2乗値」となるパワースペクトルとなる
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
    stft_frame_size,
    N_ave,
    final_time,
    acf,
    dbref,
    A
):
    # ===============================================================
    # === 周波数特性データ生成関数 (Full Scratch STFT Function版) ===
    # ===============================================================
    # time_array_after_window   : 時間領域 波形データ(正規化/オーバーラップ処理/hanning窓関数適用済)
    # samplerate                : サンプリングレート [sampling data count/s)]
    # stft_frame_size           : STFT(短時間フーリエ変換)を行う時系列データ数(=STFTフレーム長)
    # N_ave                     : オーバーラップ処理における切り出しフレーム数
    # final_time                : オーバーラップ処理で切り出したデータの最終時刻[s]
    # acf                       : 振幅補正係数(Amplitude Correction Factor)
    # dbref                     : デシベル基準値
    # A                         : 聴感補正(A特性)の有効(True)/無効(False)設定

    print("N_ave = ", N_ave)
    print("final_time = ", final_time)

    # スペクトログラムデータ格納配列の初期化
    spectrogram = []

    # 周波数軸を作成
    dt = 1 / samplerate  # サンプリング周期[s]
    # nを、stft_frame_sizeの2倍とする事で、周波数分解能をscipy.signal.spectrogramと同じとする
    # dをサンプリング周期の2倍とする(scipy.signal.spectrogramと合わせる)
    freq_bipolar = scipy.fft.fftfreq(n=(stft_frame_size * 2), d=dt)

    # freq_bipolarは、負の周波数領域軸データも含むため、
    # 「要素数(len(freq_bipolar) / 2」までの要素をスライス抽出
    freq_spctrgrm = freq_bipolar[:int(len(freq_bipolar) / 2)]
    print("freq_spctrgrm.shape = ", freq_spctrgrm.shape)
    print("np.max(freq_spctrgrm) = ", np.max(freq_spctrgrm))

    # 時間軸を作成
    # (開始:0 , 終了:オーバーラップ処理で切り出したデータの最終時刻[s],
    #  要素数:オーバーラップ処理における切り出しフレーム数)
    time_spctrgrm = np.linspace(0, final_time, N_ave)
    print("time_spctrgrm.shape = ", time_spctrgrm.shape)

    # 聴感補正曲線を計算
    a_scale = a_weighting(freq_spctrgrm)
    print("a_scale.shape = ", a_scale.shape)

    # 時間軸方向データ数分のループ処理
    for i in range(N_ave):

        # 時間領域 波形データのSTFTフレーム[i] に対して、フーリエ変換を実施
        # (scipy.fft.fft()の出力結果spectrumは複素数)
        spectrum = scipy.fft.fft(
            # xは「Input array, can be complex」
            x=time_array_after_window[i],
            # nは「Length of the transformed axis of the output」
            # nを、stft_frame_sizeの2倍とする事で、周波数分解能をscipy.signal.spectrogramと同じとする
            n=stft_frame_size * 2
        )
        # print("len(spectrum) = ", len(spectrum))

        # 振幅成分算出
        amp = np.abs(spectrum)
        # print("len(amp) = ", len(amp))

        # 振幅成分の正規化
        # 離散フーリエ変換の定義から、求まる振幅ampを入力データの振幅に合わせるため 1/N 倍して振幅を計算する。
        # 加えて、フーリエ変換された N 個のスペクトル（振幅やパワー） は、サンプリング周波数の 1/2
        # の周波数（ナイキスト周波数）を堺に左右対称となる事から、スペクトルの値は対になる対称成分を足し合わせたものが、
        # 入力データの実データと一致するため、スペクトル値をさらに2倍する正規化を施す
        amp_normalized_pre = (amp / len(time_array_after_window[i])) * 2
        # print("len(amp_normalized_pre) = ", len(amp_normalized_pre))

        # amp_normalized_preは、負の周波数領域データも含むため、
        # 「要素数(len(amp_normalized_pre) / 2」までの要素をスライス抽出
        amp_normalized = amp_normalized_pre[:int(len(amp_normalized_pre) / 2)]

        # 窓関数補正値(acf)を乗算
        amp_normaliazed_acf = amp_normalized * acf

        # dbrefが0以上の場合は、dB変換する
        if dbref > 0:
            amp_normaliazed_acf = db(
                amp_normaliazed_acf, dbref
            )

        # spectrogram配列に追加
        spectrogram.append(amp_normaliazed_acf)

    # numpy.ndarray変換を行う
    spectrogram = np.array(spectrogram)
    print("spectrogram.shape = ", spectrogram.shape)

    # dbrefが0以上、かつ、A=Trueの場合に、A特性補正を行う
    if (dbref > 0) and A:
        spectrogram = spectrogram + a_scale
        print("spectrogram.shape [dB(A)] = ", spectrogram.shape)

    # 縦軸周波数、横軸時間にするためにデータを転置
    spectrogram = spectrogram.T
    print("spectrogram.shape [dB(A) and Transposed] = ", spectrogram.shape)

    return freq_spctrgrm, time_spctrgrm, spectrogram
