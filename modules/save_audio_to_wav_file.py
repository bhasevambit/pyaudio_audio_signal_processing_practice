import os
import datetime
import soundfile as sf


def save_audio_to_wav_file(samplerate, data_normalized):
    # =====================================
    # === 音声データwavファイル保存関数 ===
    # =====================================
    now = datetime.datetime.now()

    dirname = 'wav/'
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    filename = dirname + 'recorded-sound_' + \
        now.strftime('%Y%m%d_%H%M%S') + '.wav'

    # Numpy array内の音声データをWAVファイルに保存
    sf.write(filename, data_normalized, samplerate)
