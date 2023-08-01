import pyaudio


def audio_stream_start(index, mic_mode, samplerate, frames_per_buffer):
    # ================================================
    # === Microphone入力音声ストリーム取得開始関数 ===
    # ================================================
    # index                 : 使用するマイクのdevice index
    # mic_mode              : マイクモード (1:モノラル / 2:ステレオ)
    # samplerate            : サンプリング周波数[sampling data count/s)]
    # frames_per_buffer     : 入力音声ストリームバッファあたりのサンプリングデータ数

    pa = pyaudio.PyAudio()
    print("pa = ", pa)
    print("type(pa) = ", type(pa))

    stream = pa.open(
        format=pyaudio.paInt16,
        # pyaudio.paInt16 = 16bit量子化モード (音声時間領域波形の振幅を-32767～+32767に量子化)
        channels=mic_mode,
        rate=samplerate,
        input=True,
        input_device_index=index,
        frames_per_buffer=frames_per_buffer
    )
    print("stream = ", stream)
    print("type(stream) = ", type(stream))
    print("")

    # pa        : 生成したpyaudio.PyAudioクラスオブジェクト
    #             (pyaudio.PyAudio object)
    # stream    : 生成したpyaudio.PyAudio.Streamオブジェクト
    #             (pyaudio.PyAudio.Stream object)
    return pa, stream


def audio_stream_stop(pa, stream):
    # ================================================
    # === Microphone入力音声ストリーム取得停止関数 ===
    # ================================================
    # pa        : 生成したpyaudio.PyAudioクラスオブジェクト
    #             (pyaudio.PyAudio object)
    # stream    : 生成したpyaudio.PyAudio.Streamオブジェクト
    #             (pyaudio.PyAudio.Stream object)

    # 生成したpyaudio.PyAudio.Streamオブジェクトを停止 & 終了
    stream.stop_stream()
    stream.close()

    # 生成したpyaudio.PyAudioクラスオブジェクトを削除
    pa.terminate()
