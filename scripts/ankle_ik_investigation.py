from calc_ankle import calc_ankle_angle
import numpy as np
import argparse

def investigation():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--pitch', default= 0.0)
    # parser.add_argument('--roll', default= 0.0)
    # args = parser.parse_args()

    pitch_min = -1.5
    pitch_max = 1.5
    roll_min = -1.5
    roll_max = 1.0
    interval = 0.02
    inside_limit = [-1.18, 1.18]
    outside_limit = [-1.18, 1.18]

    f = open("ankle_area.csv", "w", encoding="utf-8")

    for p in np.arange(pitch_min, pitch_max, interval):
        for r in np.arange(roll_min, roll_max, interval):
            result = calc_ankle_angle(p, r)
            if len(result) == 0:
                print(p, r, "no_result", file = f)
            else:
                if result[0] < inside_limit[0] or result[0] > inside_limit[1] or result[1] < outside_limit[0] or result[1] > inside_limit[1]:
                    print(p, r, "out_of_limit", file = f)
                else:
                    print(p, r, result[0], result[1], file = f)
    f.close()

if __name__ == "__main__":
    investigation()