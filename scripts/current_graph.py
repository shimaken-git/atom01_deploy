import pandas as pd
import matplotlib.pyplot as plt

# CSV読み込み
df = pd.read_csv("/home/kenji/current.csv", header=None)

plt.figure(figsize=(14, 8))

for i in range(df.shape[1]):
    if i == 1:
        plt.plot(
            df.index,
            df[i],
            color="red",
            linewidth=2.5,
            label="M1",
            zorder=3,
        )
    elif i == 7:
        plt.plot(
            df.index,
            df[i],
            color="blue",
            linewidth=2.5,
            label="M7",
            zorder=3,
        )
    else:
        plt.plot(
            df.index,
            df[i],
            color="gray",
            alpha=0.2,      # 薄く表示
            linewidth=0.8,
            zorder=1,
        )

plt.title("Motor Current")
plt.xlabel("Sample")
plt.ylabel("Current [A]")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()