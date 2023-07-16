import pyaudio
import numpy as np
from matplotlib import pyplot as plt


time = 1            # 計測時間[s]
samplerate = 44100  # サンプリングレート
fs = 1024           # フレームサイズ
index = 1           # マイクのチャンネル指標


def record(index, samplerate, fs, time):
    pa = pyaudio.PyAudio()
    data = []
    dt = 1 / samplerate

    # ストリームの開始
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=samplerate,
        input=True,
        input_device_index=index,
        frames_per_buffer=fs)

    # フレームサイズ毎に音声を録音していくループ
    for i in range(int(((time / dt) / fs))):
        frame = stream.read(fs)
        data.append(frame)

    # ストリームの終了
    stream.stop_stream()
    stream.close()
    pa.terminate()

    # データをまとめる処理
    data = b"".join(data)

    # データをNumpy配列に変換
    data = np.frombuffer(data, dtype="int16") / \
        float((np.power(2, 16) / 2) - 1)

    return data, i


wfm, i = record(index, samplerate, fs, time)
t = np.arange(0, fs * (i + 1) * (1 / samplerate), 1 / samplerate)

# ここからグラフ描画
# フォントの種類とサイズを設定する。
plt.rcParams['font.size'] = 14
plt.rcParams['font.family'] = 'Times New Roman'

# 目盛を内側にする。
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'

# グラフの上下左右に目盛線を付ける。
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.yaxis.set_ticks_position('both')
ax1.xaxis.set_ticks_position('both')

# 軸のラベルを設定する。
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Sound pressure [Pa]')

# データプロットの準備とともに、ラベルと線の太さ、凡例の設置を行う。
ax1.plot(t, wfm, label='signal', lw=1)

fig.tight_layout()

# グラフを表示する。
plt.show()
plt.close()
