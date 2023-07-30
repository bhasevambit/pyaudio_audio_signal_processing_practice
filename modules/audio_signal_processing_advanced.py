import scipy


def overlap(data_normalized, samplerate, stft_frame_size, overlap_rate):
    # ==============================
    # === オーバーラップ処理関数 ===
    # ==============================
    # data_normalized   : 時間領域 波形データ(正規化済)
    # samplerate        : サンプリングレート [sampling data count/s]
    # stft_frame_size   : STFT(短時間フーリエ変換)を行う時系列データ数(=STFTフレーム長)
    # overlap_rate      : オーバーラップ率 [%]

    # 全データ時間長[s]の算出
    # (= 時間領域波形データ要素数 / (サンプリングデータ数 / 秒))
    Ts = len(data_normalized) / samplerate

    # 入力音声ストリームバッファ周期[s]の算出
    # (= STFTフレーム長 / (サンプリングデータ数 / 秒) )
    Fc = stft_frame_size / samplerate

    # オーバーラップ時のずらし幅 [sampling data count]
    x_ol = stft_frame_size * (1 - (overlap_rate / 100))

    # オーバーラップ時間長[s]を算出
    overlap_time = Fc * (overlap_rate / 100)

    # 非オーバーラップ時間長[s]を算出
    non_overlap_time = Fc * (1 - (overlap_rate / 100))

    # オーバーラップ処理における切り出しフレーム数
    N_ave = int((Ts - overlap_time) / non_overlap_time)

    # 抽出したデータを入れる空配列の定義
    time_array = []

    # forループでデータを抽出
    for i in range(N_ave):
        # 切り出し位置をループ毎に更新
        ps = int(x_ol * i)

        # 切り出し位置psから入力音声ストリームバッファデータ数分抽出して配列に追加
        # (data_normalized配列に対して、開始要素: ps / 終了要素: ps+stft_frame_size / スキップ間隔: 1 でスライスしてtime_array.append)
        time_array.append(data_normalized[ps:ps + stft_frame_size:1])

        # 切り出したデータの最終時刻[s]
        # (= (切り出し位置 + STFTフレーム長) / (サンプリングデータ数 / 秒) )
        final_time = (ps + stft_frame_size) / samplerate

    return time_array, N_ave, final_time


def hanning(time_array, stft_frame_size, N_ave):
    # =============================================
    # === Hanning窓関数 (振幅補正係数計算付き) ===
    # =============================================
    # time_array        : オーバーラップ抽出された時間領域波形配列(正規化済)
    # stft_frame_size   : STFT(短時間フーリエ変換)を行う時系列データ数(=STFTフレーム長)
    # N_ave             : オーバーラップ処理における切り出しフレーム数

    # Hanning窓 作成
    han = scipy.signal.hann(stft_frame_size)

    # 振幅補正係数(Amplitude Correction Factor)
    acf = 1 / (sum(han) / stft_frame_size)

    # 時間領域 波形データ(正規化/オーバーラップ処理/hanning窓関数適用済)の初期化
    time_array_after_window = [0 for _ in range(len(time_array))]

    # オーバーラップされた複数時間波形全てに窓関数をかける
    for i in range(N_ave):
        time_array_after_window[i] = time_array[i] * han         # 窓関数をかける

    return time_array_after_window, acf
