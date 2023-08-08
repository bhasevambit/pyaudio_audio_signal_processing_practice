import datetime
import os

import soundfile as sf


def save_audio_to_wav_file(samplerate, audio_discrete_data):
    # =====================================
    # === 音声データwavファイル保存関数 ===
    # =====================================
    # samplerate                : サンプリング周波数 [sampling data count/s)]
    # audio_discrete_data       : 音声データ(時系列離散データ) 1次元配列

    print("Audio DATA File Save START")

    now = datetime.datetime.now()

    dirname = 'wav/'
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    filename = dirname + 'recorded-sound_' + \
        now.strftime('%Y%m%d_%H%M%S') + '.wav'

    # Numpy array内の音声データをWAVファイルとして保存
    sf.write(filename, audio_discrete_data, samplerate)

    print("Audio DATA File Save END\n")

    # filename : 保存した音声データをWAVファイル名(拡張子あり)
    return filename
