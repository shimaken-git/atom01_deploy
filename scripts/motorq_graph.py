import argparse

import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(
        description="Plot all motor data from CSV"
    )

    parser.add_argument(
        "csv_file",
        help="CSV file containing motor data"
    )

    args = parser.parse_args()

    csv_file = args.csv_file
    filename = csv_file.lower()

    # =========================
    # ファイル名からデータ種別を判定
    # =========================
    if "current" in filename:
        ylabel = "Torque [Nm]"
        title = "Motor Torque"

    elif "position" in filename:
        ylabel = "Position [rad]"
        title = "Motor Position"

    elif "action" in filename:
        ylabel = "Position [rad]"
        title = "Motor Action"
    
    else:
        raise ValueError(
            "CSV filename must contain 'current' or 'position'"
        )

    # CSV読み込み
    df = pd.read_csv(csv_file, header=None)

    # =========================
    # モーターのグループ
    # =========================
    motor_groups = [
        range(0, 6),    # M0 ～ M5
        range(6, 13),   # M6 ～ M12
        range(13, 18),  # M13 ～ M17
        range(18, 23),  # M18 ～ M22
    ]

    # =========================
    # グラフ作成
    # =========================
    fig, axes = plt.subplots(
        nrows=1,
        ncols=4,
        figsize=(20, 8),
        sharex=True
    )

    for ax, motors in zip(axes, motor_groups):

        for motor_id in motors:

            if motor_id >= df.shape[1]:
                continue

            ax.plot(
                df.index,
                df.iloc[:, motor_id],
                linewidth=1.0,
                alpha=0.7,
                label=f"M{motor_id}"
            )

        motor_list = list(motors)

        ax.set_title(
            f"M{motor_list[0]} ～ M{motor_list[-1]}"
        )

        ax.set_xlabel("Sample")
        ax.set_ylabel(ylabel)

        ax.grid(True)
        ax.legend(fontsize=8)

    fig.suptitle(title, fontsize=16)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()