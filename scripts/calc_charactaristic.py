import glob
import os
import re

import numpy as np
import pandas as pd

from scipy.signal import correlate

results = []

files = sorted(glob.glob("sin_*Hz.csv"))

for file in files:

    m = re.search(r"sin_(.*)Hz.csv", os.path.basename(file))
    freq = float(m.group(1))

    df = pd.read_csv(file)

    t = df["time"].values
    cmd = df["command(rad)"].values
    pos = df["position(rad)"].values

    # DC成分除去
    cmd = cmd - np.mean(cmd)
    pos = pos - np.mean(pos)

    # 振幅
    amp_cmd = (cmd.max() - cmd.min()) / 2
    amp_pos = (pos.max() - pos.min()) / 2

    gain = amp_pos / amp_cmd

    # クロスコリレーション
    corr = correlate(pos, cmd)

    lag = np.argmax(corr) - (len(cmd)-1)

    dt = np.mean(np.diff(t))

    delay = lag * dt

    phase = delay * freq * 360

    results.append([
        freq,
        gain,
        phase,
        delay*1000
    ])

result = pd.DataFrame(
    results,
    columns=[
        "freq(Hz)",
        "gain",
        "phase(deg)",
        "delay(ms)"
    ]
)

print(result)

result.to_csv("frequency_response.csv", index=False)