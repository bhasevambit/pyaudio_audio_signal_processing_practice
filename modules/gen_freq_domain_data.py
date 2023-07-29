import scipy
import numpy as np
from modules.a_weighting import a_weighting


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
        with np.errstate(divide='ignore'):
            amp_normalized = 20 * np.log10(amp_normalized / dbref)

        # dB変換されていてAがTrueの時に聴感補正する
        if A:
            amp_normalized += a_weighting(freq)

    return spectrum, amp_normalized, phase, freq


def get_freq_domain_data_of_signal_spctrgrm(
    data_normalized, samplerate, frames_per_buffer, overlap_rate, dbref, A
):

    freq_spctrgrm, time_spctrgrm, spectrogram = scipy.signal.spectrogram(
        data_normalized,
        fs=samplerate,
        window="hann",  # 窓関数はHanning窓を使用
        nperseg=1024,
        # noverlapはオーバラップするサンプリングデータ数
        noverlap=(frames_per_buffer * (overlap_rate / 100)),
        nfft=44100,
        # scalingは"spectrum"を指定する事でスペクトログラムデータ単位が「振幅の2乗」となるパワースペクトルとなる
        scaling="spectrum",
        # modeを"magnitude"とすることで、スペクトログラムデータとして振幅が算出される
        mode="magnitude"
    )

    # dbrefが0以上の時にdB変換する
    if dbref > 0:
        with np.errstate(divide='ignore'):
            spectrogram = 20 * np.log10(spectrogram / dbref)

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
    # time_array_after_window   : 時間領域 波形データ(正規化/オーバーラップ処理/hanning窓関数適用済)
    # samplerate                : サンプリングレート [sampling data count/s)]
    # frames_per_buffer         : 入力音声ストリームバッファあたりのサンプリングデータ数
    # N_ave                     : オーバーラップ処理における切り出しフレーム数
    # acf                       : 振幅補正係数(Amplitude Correction Factor)
    # dbref                     : デシベル基準値
    # A                         : 聴感補正(A特性)の有効(True)/無効(False)設定

    # dB(デシベル）演算関数
    def db(x, dbref):
        y = 20 * np.log10(x / dbref)                   # 変換式
        return y                                       # dB値を返す

    if dbref > 0 and A:
        # デシベル基準値設定あり、かつ、聴感補正(A特性)の有効の場合
        no_db_a = False
    else:
        no_db_a = True

    # 平均化FFTする関数
    fft_array = []

    # 周波数軸を作成
    freq_spctrgrm = np.linspace(0, samplerate, frames_per_buffer)

    # 聴感補正曲線を計算
    a_scale = a_weighting(freq_spctrgrm)

    # FFTをして配列にdBで追加、窓関数補正値をかけ、(frames_per_buffer/2)の正規化を実施
    for i in range(N_ave):

        if no_db_a:
            # 非dB(A)モード
            fft_array.append(
                acf *
                np.abs(scipy.fft.fft(time_array_after_window[i]) /
                       (frames_per_buffer / 2))
            )

        else:
            # dB(A)モード
            fft_array.append(
                db(
                    acf *
                    np.abs(scipy.fft.fft(time_array_after_window[i]) /
                           (frames_per_buffer / 2)),
                    dbref
                )
            )

    # 型をndarrayに変換し、A特性をかける
    # (A特性はdB表示しない場合はかけない）
    if no_db_a:
        # 非dB(A)モード
        fft_array = np.array(fft_array)
    else:
        # dB(A)モード
        fft_array = np.array(fft_array) + a_scale

    # 全てのFFT波形の平均を計算
    fft_mean = np.mean(
        np.sqrt(
            fft_array ** 2),
        axis=0)

    return fft_array, fft_mean, freq_spctrgrm
