def get_selected_mode_by_std_input(mode_count):
    # ============================================
    # === 標準入力にて選択されたモード取得関数 ===
    # ============================================
    # mode_count : 選択するモード数 (例：0,1を選択させる場合は"2")

    # input関数で入力された値を変数input_modeに代入
    input_mode = input(">>> Please INPUT Mode : ")

    try:
        input_mode = int(input_mode)

    except BaseException:
        print("\n!!! Input Value Error, please Re-Input !!!\n")
        return get_selected_mode_by_std_input(mode_count)

    if (input_mode < 0) or (input_mode > (mode_count - 1)):
        print("\n!!! Invalid input value range, please Re-Input !!!\n")
        return get_selected_mode_by_std_input(mode_count)

    else:
        # input_mode : 標準入力されたモード
        return input_mode


def get_strings_by_std_input():
    # ============================================
    # === 標準入力にて入力された文字列取得関数 ===
    # ============================================

    # input関数で入力された文字列を変数input_stringsに代入
    input_strings = input(">>> Please INPUT : ")

    try:
        input_strings = str(input_strings)

    except BaseException:
        print("\n!!! Input Value Error, please Re-Input !!!\n")
        return get_selected_mode_by_std_input(input_strings)

    else:
        # input_strings : 標準入力された文字列
        return input_strings
