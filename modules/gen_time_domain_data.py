import math

from modules.audio_stream import gen_discrete_data_from_audio_stream
from modules.audio_signal_processing_basic import discrete_data_normalize
from modules.audio_signal_processing_basic import gen_time_axis_data


def gen_time_domain_data(stream, frames_per_buffer, samplerate, time):
    # ==============================================
    # === 時間領域波形データ生成関数(時間指定版) ===
    # ==============================================
    # stream                : マイク入力音声データストリーム
    # frames_per_buffer     : 入力音声ストリームバッファあたりのサンプリングデータ数
    # samplerate            : サンプリングレート [sampling data count/s)]
    # time                  : 録音時間[s] ("0"の場合は、リアルタイムモードとしてデータ生成)

    if time > 0:
        # ==========================
        # === 録音時間指定モード ===
        # ==========================

        # 時間領域波形 離散データ 1次元配列を格納する配列の初期化
        audio_data_united = []
        # ループ変数初期化
        i = 0

        # サンプリング周期[s]の算出
        dt = 1 / samplerate

        print("Audio Stream Recording START")

        # 入力音声ストリームバッファ毎に時間領域波形 離散データ 1次元配列を生成
        for i in range(int(((time / dt) / frames_per_buffer))):
            # 標準出力への経過時間表示
            erapsed_time = math.floor(
                ((i * frames_per_buffer) / samplerate) * 100) / 100
            print("  - Erapsed Time[s]: ", erapsed_time)

            # 時間領域波形 離散データ 1次元配列 生成の生成
            audio_data_per_buffer = gen_discrete_data_from_audio_stream(
                stream, frames_per_buffer
            )

            audio_data_united.append(audio_data_per_buffer)

        print("Audio Stream Recording END\n")

        # 入力音声ストリームバッファ毎の時間領域波形 離散データ 1次元配列を連結
        # (入力音声ストリームバッファ毎に、要素が分かれていたdataを、要素間でbyte列連結)
        audio_discrete_data = b"".join(audio_data_united)
        print("Length of Discrete All-DATA = ", len(audio_discrete_data))
        print("")

    else:
        # ==========================
        # === リアルタイムモード ===
        # ==========================

        # 時間領域波形 離散データ 1次元配列 生成の生成
        audio_discrete_data = gen_discrete_data_from_audio_stream(
            stream, frames_per_buffer
        )
        print(
            "Length of Discrete DATA per Buffer = ",
            len(audio_discrete_data)
        )

    # 時間領域波形データの正規化
    data_normalized = discrete_data_normalize(audio_discrete_data, "int16")

    # 時間領域波形データ(正規化済)に対応した時間軸データを作成
    time_normalized = gen_time_axis_data(data_normalized, samplerate)

    # data_normalized : 時間領域波形データ(正規化済)
    # time_normalized : 時間領域波形データ(正規化済)に対応した時間軸データ
    return data_normalized, time_normalized
