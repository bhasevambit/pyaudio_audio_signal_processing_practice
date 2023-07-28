import scipy


def hanning(time_array, frames_per_buffer, N_ave):
    # =============================================
    # === Hanning窓関数 (振幅補正係数計算付き) ===
    # =============================================
    # time_array        : オーバーラップ抽出された時間領域波形配列(正規化済)
    # frames_per_buffer : 入力音声ストリームバッファあたりのサンプリングデータ数
    # N_ave             : オーバーラップ処理における切り出しフレーム数

    # Hanning窓 作成
    han = scipy.signal.hann(frames_per_buffer)

    # 振幅補正係数(Amplitude Correction Factor)
    acf = 1 / (sum(han) / frames_per_buffer)

    # 時間領域 波形データ(正規化/オーバーラップ処理/hanning窓関数適用済)の初期化
    time_array_after_window = [0 for _ in range(len(time_array))]

    # オーバーラップされた複数時間波形全てに窓関数をかける
    for i in range(N_ave):
        time_array_after_window[i] = time_array[i] * han         # 窓関数をかける

    return time_array_after_window, acf
