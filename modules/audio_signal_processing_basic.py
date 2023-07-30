import numpy as np


def db(x, dbref):
    # ==============================
    # === 音圧レベル[dB]演算関数 ===
    # ==============================
    # x     : 観測値[pa]
    # dbref : 基準値[pa]

    # dbref[pa]を基準としたx[pa]の音圧レベル[dB]の算出
    with np.errstate(divide='ignore'):
        y = 20 * np.log10(x / dbref)

    return y


def a_weighting(f):
    # ==================================
    # === 聴感補正関数 (A特性カーブ) ===
    # ==================================
    # f : 周波数特性 X軸向けデータ

    if f[0] == 0:
        f[0] = 1e-6
    else:
        pass

    ra = (np.power(12194, 2) * np.power(f, 4)) / \
         ((np.power(f, 2) + np.power(20.6, 2)) *
          np.sqrt((np.power(f, 2) + np.power(107.7, 2)) *
                  (np.power(f, 2) + np.power(737.9, 2))) *
          (np.power(f, 2) + np.power(12194, 2)))

    a = 20 * np.log10(ra) + 2.00

    return a
