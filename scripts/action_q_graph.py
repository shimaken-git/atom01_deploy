import argparse

import pandas as pd
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(
        description="Plot motor q and action from CSV files"
    )

    parser.add_argument(
        "q_csv",
        help="CSV file containing motor q"
    )

    parser.add_argument(
        "action_csv",
        help="CSV file containing motor action"
    )

    parser.add_argument(
        "motor_id",
        type=int,
        help="Motor ID to plot"
    )

    args = parser.parse_args()

    # CSV読み込み
    q_df = pd.read_csv(args.q_csv, header=None)
    action_df = pd.read_csv(args.action_csv, header=None)

    motor_id = args.motor_id

    # モーターIDチェック
    if motor_id < 0:
        raise ValueError("motor_id must be >= 0")

    if motor_id >= q_df.shape[1]:
        raise ValueError(
            f"Motor ID {motor_id} is not available in q CSV"
        )

    if motor_id >= action_df.shape[1]:
        raise ValueError(
            f"Motor ID {motor_id} is not available in action CSV"
        )

    # データ取得
    q = q_df.iloc[:, motor_id]
    action = action_df.iloc[:, motor_id]

    # qを5点に1点に間引く
    q_decimated = q.iloc[::5].reset_index(drop=True)

    # actionとqの長さを合わせる
    length = min(len(q_decimated), len(action))

    q_decimated = q_decimated.iloc[:length]
    action = action.iloc[:length]

    # グラフ
    plt.figure(figsize=(14, 7))

    plt.plot(
        q_decimated.index,
        q_decimated,
        linewidth=1.5,
        label=f"q M{motor_id}"
    )

    plt.plot(
        action.index,
        action,
        linewidth=1.5,
        label=f"action M{motor_id}"
    )

    plt.title(f"Motor {motor_id}: q vs action")
    plt.xlabel("Sample")
    plt.ylabel("Value")

    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()