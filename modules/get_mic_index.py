import pyaudio


def get_mic_index():
    # ================================
    # === Microphone Index取得関数 ===
    # ================================
    pa = pyaudio.PyAudio()
    mic_list = []

    print("=== Audio Input Devices (Microphone) ===\n")

    for host_index in range(0, pa.get_host_api_count()):  # Host APIで大分類

        host_api_info = pa.get_host_api_info_by_index(host_index)
        print(
            "  --- Host API :",
            host_api_info["name"],
            "[INDEX:",
            host_api_info["index"],
            ", Default-device-index:",
            host_api_info["defaultOutputDevice"],
            "] ---"
        )

        for device_index in range(
                0, pa.get_host_api_info_by_index(host_index)['deviceCount']
        ):  # Deviceで小分類

            dev_info = pa.get_device_info_by_host_api_device_index(
                host_index,
                device_index
            )

            if dev_info["maxInputChannels"] != 0:
                print(
                    "  index:",
                    dev_info["index"],
                    " ",
                    dev_info["name"],
                    "( IN-Ch:",
                    dev_info["maxInputChannels"],
                    "/ OUT-Ch:",
                    dev_info["maxOutputChannels"],
                    ")"
                )
                mic_list.append(
                    pa.get_device_info_by_index(device_index)['index'])

        print("")

    return mic_list
