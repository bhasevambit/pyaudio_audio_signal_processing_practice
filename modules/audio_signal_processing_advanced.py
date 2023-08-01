import scipy


def overlap(discrete_data, samplerate, stft_frame_size, overlap_rate):
    # ==============================
    # === オーバーラップ処理関数 ===
    # ==============================
    # discrete_data     : 離散データ 1次元配列
    # samplerate        : サンプリング周波数 [sampling data count/s]
    # stft_frame_size   : STFT(短時間フーリエ変換)を行う離散データ数(=STFTフレーム長)
    # overlap_rate      : オーバーラップ率 [%]

    # 全離散データ時間長 Ts[s]の算出
    # (= 離散データ要素数 / (サンプリングデータ数 / 秒))
    Ts = len(discrete_data) / samplerate

    # STFTフレーム周期 Tf[s]の算出
    # (= STFTフレーム長 / (サンプリングデータ数 / 秒) )
    Tf = stft_frame_size / samplerate

    # オーバーラップ時のずらし幅 x_ol[sampling data count]
    x_ol = stft_frame_size * (1 - (overlap_rate / 100))

    # オーバーラップ時間長 overlap_time[s]を算出
    overlap_time = Tf * (overlap_rate / 100)

    # 非オーバーラップ時間長 non_overlap_time[s]を算出
    non_overlap_time = Tf - overlap_time

    # オーバーラップ処理における切り出しフレーム数
    N_ave = int((Ts - overlap_time) / non_overlap_time)

    # オーバーラップ処理後 離散データ 1次元配列の初期化
    data_overlaped = []

    # forループでデータを抽出
    for i in range(N_ave):
        # 切り出し位置をループ毎に更新
        ps = int(x_ol * i)

        # 切り出し位置psから入力音声ストリームバッファデータ数分抽出して配列に追加
        # (discrete_data配列に対して、開始要素: ps / 終了要素: ps+stft_frame_size / スキップ間隔: 1 でスライスしてdata_overlaped.append)
        data_overlaped.append(discrete_data[ps:ps + stft_frame_size:1])

        # 切り出したデータの最終時刻[s]
        # (= (切り出し位置 + STFTフレーム長) / (サンプリングデータ数 / 秒) )
        final_time = (ps + stft_frame_size) / samplerate

    # data_overlaped    : オーバーラップ処理後 離散データ 1次元配列
    # N_ave             : オーバーラップ処理における切り出しフレーム数
    # final_time        : オーバーラップ処理後 離散データの最終時刻[s]
    return data_overlaped, N_ave, final_time


def window(data_overlaped, stft_frame_size, N_ave, window_func):
    # =============================================
    # === Hanning窓関数 (振幅補正係数計算付き) ===
    # =============================================
    # data_overlaped    : オーバーラップ処理後 離散データ 1次元配列
    # stft_frame_size   : STFT(短時間フーリエ変換)を行う離散データ数(=STFTフレーム長)
    # N_ave             : オーバーラップ処理における切り出しフレーム数

    # 窓関数 1次元配列の作成
    if window_func == "hann":
        # Hanning窓
        window = scipy.signal.hann(stft_frame_size)
    else:
        # 矩形窓
        window = scipy.signal.boxcar(stft_frame_size)

    # 振幅補正係数(Amplitude Correction Factor)
    acf = 1 / (sum(window) / stft_frame_size)

    # 窓関数適用後 離散データ 1次元配列の初期化
    data_applied_window = [0 for _ in range(len(data_overlaped))]

    # オーバーラップ処理における切り出しフレームの個々に窓関数を適用
    for i in range(N_ave):

        # 切り出しフレーム(numpy.ndarray)と窓関数(numpy.ndarray)を要素毎に乗算
        data_applied_window[i] = data_overlaped[i] * window

    # data_applied_window   : 窓関数適用後 離散データ 1次元配列
    # acf                   : 振幅補正係数(Amplitude Correction Factor)
    return data_applied_window, acf
