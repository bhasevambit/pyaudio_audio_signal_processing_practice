import pyaudio


def audio_stream_start(index, mic_mode, samplerate, frames_per_buffer):
    # ================================================
    # === Microphone入力音声ストリーム取得開始関数 ===
    # ================================================
    # index                 : 使用するマイクのdevice index
    # mic_mode              : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate            : サンプリングレート[sampling data count/s)]
    # frames_per_buffer     : 入力音声ストリームバッファあたりのサンプリングデータ数

    pa = pyaudio.PyAudio()

    stream = pa.open(
        format=pyaudio.paInt16,
        # pyaudio.paInt16 = 16bit量子化モード (音声時間領域波形の振幅を-32767～+32767に量子化)
        channels=mic_mode,
        rate=samplerate,
        input=True,
        input_device_index=index,
        frames_per_buffer=frames_per_buffer
    )

    return pa, stream


def audio_stream_stop(pa, stream):
    # ================================================
    # === Microphone入力音声ストリーム取得停止関数 ===
    # ================================================
    stream.stop_stream()
    stream.close()
    pa.terminate()
