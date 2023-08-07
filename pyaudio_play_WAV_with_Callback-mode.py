# ========================================
# === Play WAV File with Callback-mode ===
# ========================================
import sys
import time
import wave

import pyaudio

CHUNK = 1024

if len(sys.argv) < 2:
    print(f'Plays a wave file. Usage: {sys.argv[0]} filename.wav')
    sys.exit(-1)

with wave.open(sys.argv[1], 'rb') as wf:  # mode="rb" is read-only mode

    # ====================================
    # === Define callback for playback ===
    # ====================================
    def callback(in_data, frame_count, time_info, status):
        # PyAudio will call a user-defined callback function whenever it
        # needs new audio data to play and/or when new recorded audio data
        # becomes available. PyAudio calls the callback function in a separate
        # thread. The callback function must have the following signature
        # callback(<input_data>, <frame_count>, <time_info>, <status_flag>). It
        # must return a tuple containing frame_count frames of audio data to
        # output (for output streams) and a flag signifying whether there are
        # more expected frames to play or record. (For input-only streams, the
        # audio data portion of the return value is ignored.)
        data = wf.readframes(frame_count)
        # If len(data) is less than requested frame_count, PyAudio
        # automatically assumes the stream is finished, and the stream stops.
        return (data, pyaudio.paContinue)

    # === Instantiate PyAudio and initialize PortAudio system resources ===
    p = pyaudio.PyAudio()

    # === Open stream using callbac ===
    # The audio stream starts processing once the stream is opened, which
    # will call the callback function repeatedly until that function returns
    # "pyaudio.paComplete" or "pyaudio.paAbort", or until either
    # "pyaudio.PyAudio.Stream.stop" or "pyaudio.PyAudio.Stream.close" is called.
    # Note that if the callback returns fewer frames than the frame_count
    # argument, the stream automatically closes after those frames are played.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)

    # === Wait for stream to finish ===
    # To keep the stream active, the main thread must remain alive, e.g., by
    # sleeping. In the example above, once the entire wavefile is read,
    # "wf.readframes(frame_count)" will eventually return fewer than the
    # requested frames. The stream will stop, and the while loop will end.
    while stream.is_active():
        time.sleep(0.1)

    # === Close stream ===
    stream.close()

    # === Release PortAudio system resources ===
    p.terminate()
