import pyaudio


def audio_stream_start(index, mic_mode, samplerate, fs):
    # ============================================
    # === Microphone入力音声ストリーム生成関数 ===
    # ============================================
    # index : 使用するマイクのdevice index
    # mic_mode : mic_mode : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate : サンプリングレート[sampling data count/s)]
    # fs : フレームサイズ[sampling data count/frame]

    pa = pyaudio.PyAudio()

    # ストリームの開始
    stream = pa.open(
        format=pyaudio.paInt16,
        # pyaudio.paInt16 = 16bit量子化モード (音声時間領域波形の振幅を-32767～+32767に量子化)
        channels=mic_mode,
        rate=samplerate,
        input=True,
        input_device_index=index,
        frames_per_buffer=fs
    )

    return pa, stream
