import argparse
import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(
        description="Plot ang_vel and gravity_b from observation CSV"
    )

    parser.add_argument(
        "filename",
        help="Path to observation CSV file"
    )

    parser.add_argument(
        "--dt",
        type=float,
        default=0.02,
        help="Sampling period [s] (default: 0.02 = 50 Hz)"
    )

    args = parser.parse_args()

    # CSV読み込み
    df = pd.read_csv(args.filename, header=None)

    if df.shape[1] < 6:
        raise ValueError(
            f"CSVには少なくとも6列必要です。現在: {df.shape[1]}列"
        )

    # 先頭3列: ang_vel
    ang_vel = df.iloc[:, 6:9].to_numpy()

    # 次の3列: gravity_b
    gravity_b = df.iloc[:, 3:6].to_numpy()

    # 時間軸
    time = df.index.to_numpy() * args.dt

    axis_names = ["X", "Y", "Z"]

    # X, Y, Z の色
    colors = ["red", "green", "blue"]

    # ==========================================
    # Window 1 : ang_vel
    # ==========================================

    fig1, axes1 = plt.subplots(
        3,
        1,
        figsize=(12, 8),
        sharex=True
    )

    for i, axis in enumerate(axis_names):
        axes1[i].plot(
            time,
            ang_vel[:, i],
            color=colors[i],
            label=f"ang_vel_{axis.lower()}"
        )

        axes1[i].set_ylabel(axis)
        axes1[i].grid(True)
        axes1[i].legend(loc="upper right")

    axes1[0].set_title("Angular Velocity")
    axes1[-1].set_xlabel("Time [s]")

    fig1.tight_layout()

    # ==========================================
    # Window 2 : gravity_b
    # ==========================================

    fig2, axes2 = plt.subplots(
        3,
        1,
        figsize=(12, 8),
        sharex=True
    )

    for i, axis in enumerate(axis_names):
        axes2[i].plot(
            time,
            gravity_b[:, i],
            color=colors[i],
            label=f"gravity_b_{axis.lower()}"
        )

        axes2[i].set_ylabel(axis)
        axes2[i].grid(True)
        axes2[i].legend(loc="upper right")

    axes2[0].set_title("Gravity Vector")
    axes2[-1].set_xlabel("Time [s]")

    fig2.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()