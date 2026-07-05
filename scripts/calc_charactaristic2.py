import glob
import os
import re

import numpy as np
import pandas as pd

from scipy.optimize import curve_fit
from scipy.signal import correlate

#########################################################################
# 一次遅れモデル
#########################################################################

def gain_model(f, tau, k):
    w = 2*np.pi*f
    return k / np.sqrt(1 + (w*tau)**2)

#########################################################################
# CSV解析
#########################################################################

results = []

files = sorted(glob.glob("sin_*Hz.csv"))

for file in files:

    freq = float(
        re.search(r"sin_(.*)Hz.csv",
        os.path.basename(file)).group(1)
    )

    df = pd.read_csv(file)

    t = df["time"].values

    cmd = df["command(rad)"].values
    pos = df["position(rad)"].values

    cmd -= np.mean(cmd)
    pos -= np.mean(pos)

    amp_cmd = (cmd.max()-cmd.min())/2
    amp_pos = (pos.max()-pos.min())/2

    gain = amp_pos / amp_cmd

    corr = correlate(pos, cmd)

    lag = np.argmax(corr) - (len(cmd)-1)

    dt = np.mean(np.diff(t))

    delay = lag*dt

    phase = delay * freq * 360

    results.append([
        freq,
        gain,
        phase,
        delay
    ])

result = pd.DataFrame(
    results,
    columns=[
        "freq",
        "gain",
        "phase",
        "delay"
    ]
)

#########################################################################
# 一次遅れフィッティング
#########################################################################

freq = result["freq"].values
gain = result["gain"].values

popt,_ = curve_fit(
    gain_model,
    freq,
    gain,
    p0=[0.02,1.0]
)

tau = popt[0]
k = popt[1]

#########################################################################
# Bandwidth
#########################################################################

bandwidth = 1/(2*np.pi*tau)

#########################################################################
# Delay
#########################################################################

delay = result["delay"].mean()

#########################################################################
# 表示
#########################################################################

print(result)

print()

print("===================================")
print("Isaac Lab Parameters")
print("===================================")

print(f"DC Gain      : {k:.3f}")

print(f"TimeConst    : {tau:.4f} s")

print(f"Bandwidth    : {bandwidth:.2f} Hz")

print(f"Delay        : {delay:.4f} s")