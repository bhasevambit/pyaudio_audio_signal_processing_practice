import wave
import sys

import pyaudio


CHUNK = 1024

if len(sys.argv) < 2:
    print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
    sys.exit(-1)

with wave.open(sys.argv[1], 'rb') as wf:  # mode="rb" is read-only mode

    # === Instantiate PyAudio and initialize PortAudio system resources ===
    p = pyaudio.PyAudio()

    # === Open stream ===
    # To record or play audio, open a stream on the desired device with the
    # desired audio parameters using "pyaudio.PyAudio.open()". This sets up a
    # "pyaudio.PyAudio.Stream" to play or record audio.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # === Play Audio from the wave file ===
    # Play audio by writing audio data to the stream using
    # "pyaudio.PyAudio.Stream.write()". Note that in “blocking mode”, each
    # "pyaudio.PyAudio.Stream.write()" or "pyaudio.PyAudio.Stream.read()"
    # blocks until all frames have been played/recorded. An alternative
    # approach is “callback mode”, described below, in which PyAudio invokes a
    # user-defined function to process recorded audio or generate output
    # audio.
    while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
        stream.write(data)

    # === Close stream ===
    stream.close()

    # === Release PortAudio system resources ===
    p.terminate()
