import math


def audio_recode(stream, samplerate, fs, time):
    # ============================================
    # === Microphone入力音声レコーディング関数 ===
    # ============================================
    # samplerate    : サンプリングレート[sampling data count/s)]
    # fs            : フレームサイズ[sampling data count/frame]
    # pa            : pyaudioクラスオブジェクト
    # stream        : マイク入力音声ストリーム
    # time          : 録音時間[s]

    # フレームサイズ毎に音声を録音していくループ
    print("Recording START")
    data = []
    dt = 1 / samplerate
    i = 0

    for i in range(int(((time / dt) / fs))):
        erapsed_time = math.floor(((i * fs) / samplerate) * 100) / 100
        print("  - Erapsed Time[s]: ", erapsed_time)

        frame = stream.read(fs)
        data.append(frame)

    print("Recording STOP\n")

    return data
