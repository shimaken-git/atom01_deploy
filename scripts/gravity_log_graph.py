import argparse
import re
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    description="Plot gravity_b from log file")
parser.add_argument(
    "csv_file",
    help="CSV file path"
)

args = parser.parse_args()
log_file = args.csv_file

# データ格納用
gx = []
gy = []
gz = []

# gravity_b の値を抽出
pattern = re.compile(
    r"gravity_b:\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
)

with open(log_file, "r") as f:
    for line in f:
        m = pattern.search(line)
        if m:
            gx.append(float(m.group(1)))
            gy.append(float(m.group(2)))
            gz.append(float(m.group(3)))

# サンプル番号
t = range(len(gx))

# プロット
plt.figure(figsize=(10, 5))
plt.plot(t, gx, label="gravity_x")
plt.plot(t, gy, label="gravity_y")
plt.plot(t, gz, label="gravity_z")

plt.xlabel("Sample")
plt.ylabel("Gravity")
plt.title("gravity_b")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
