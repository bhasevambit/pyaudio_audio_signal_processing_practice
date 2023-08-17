import wave

import librosa
import matplotlib.pyplot as plt
import numpy as np
import pysptk as sptk
import pyworld as pw

if __name__ == '__main__':
    # =================
    # === Main Code ===
    # =================

    # 音声ファイル
    audio_path = "./a.wav"

    # 読み込みモードでWAVファイルを開く
    with wave.open(audio_path, 'rb') as wr:

        # 情報取得
        ch = wr.getnchannels()
        width = wr.getsampwidth()
        fr = wr.getframerate()
        fn = wr.getnframes()

        # 表示
        print("チャンネル: ", ch)
        print("サンプルサイズ: ", width)
        print("サンプリングレート: ", fr)
        print("フレームレート: ", fn)
        print("再生時間: ", 1.0 * fn / fr)

    # librosaで音声ファイルを読み込み
    y, sr = librosa.load(audio_path, sr=fr)

    # pyworldでスペクトル包絡を取得
    y = y.astype(np.float)
    _f0, t = pw.dio(y, sr)
    f0 = pw.stonemask(y, _f0, t, sr)
    sp = pw.cheaptrick(y, f0, t, sr)
    ap = pw.d4c(y, f0, t, sr)

    # 元の音声のスペクトル包絡
    center_sp = int(len(sp) / 2)  # 定常部分を求める

    # メルケプストラムの算出
    mcep = sptk.sp2mc(sp, order=19, alpha=0.42)
    center_mcep = int(len(mcep) / 2)  # 定常部分を求める

    # メルケプストラムからスペクトル包絡に変換
    sp_from_mcep = sptk.mc2sp(mcep, alpha=0.42, fftlen=1024)

    # グラフの表示
    # メルケプストラム
    plt.figure()
    plt.plot(mcep[center_sp])
    plt.title('Mel-cepstrum')
    # "元のスペクトル包絡"と"メルケプストラムから再合成したスペクトル包絡"
    plt.figure()
    plt.plot(np.log10(sp[center_sp]), label="Original")
    plt.plot(np.log10(sp_from_mcep[center_sp]), label="Conversion")
    plt.title('spectral envelope')
    plt.legend()

    print("=================")
    print("= Main Code END =")
    print("=================\n")
