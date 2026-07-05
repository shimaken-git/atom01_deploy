import time
import math
import csv
import motors_py

# ======================================================
# パラメータ
# ======================================================

MOTOR_LIST = {
    "joint1": (1, -1, 30.0, 0.5),
    "joint2": (2, -1, 30.0, 0.5),
    "joint3": (3, 1, 30.0, 0.5),
    "joint4": (4, -1, 50.0, 1.0),
}

CONTROL_PERIOD = 0.003      # 500Hz

FREQ_LIST = [
    0.1,
    0.2,
    0.5,
    1.0,
    2.0,
]

SIN_AMPLITUDE = math.radians(10)   # ±10deg
TEST_TIME = 20.0            # sec

MOVE_TIME = 5.0             # ゆっくり移動時間

# テストする関節
TEST_JOINT = "joint4"   # knee pitch

# 初期姿勢
TARGET_POSTURE = {
    "joint2": 0.0,                 # hip roll
    "joint1": math.radians(-90),   # hip pitch
    "joint3": 0.0,                 # hip yaw
    "joint4": math.radians(90),    # ぶら下げ状態
}

current_pos = {}
chara = {}

# ======================================================
# SDK依存部（置き換える）
# ======================================================

def read_joint(name):
    """
    return
        position(rad)
        velocity(rad/s)
        torque(Nm or estimated torque)
    """
    q = motors[name].get_motor_pos() * chara[name][1]
    dq = motors[name].get_motor_spd() * chara[name][1]
    tau = motors[name].get_motor_current() * chara[name][1]
    
    return q, dq, tau


def command_position(name, pos):
    motors[name].motor_mit_cmd(pos * chara[j][1], 0, chara[j][2], chara[j][3], 0)


def torque_off():
    for j in motors.keys():
        print("モーターを無効にする...")
        motors[j].deinit_motor()


# ======================================================
# 補助関数
# ======================================================

def wait_key(msg):
    input(f"\n{msg}  [Enter]")


def move_slow(targets, duration):

    start = {}

    for j in targets.keys():
        start[j] = motors[j].get_motor_pos() * chara[j][1]

    t0 = time.time()

    while True:

        t = time.time() - t0
        r = min(t / duration, 1.0)

        # cosine interpolation
        s = 0.5 - 0.5 * math.cos(math.pi * r)

        for j in targets.keys():

            cmd = start[j] + (targets[j] - start[j]) * s
            motors[j].motor_mit_cmd(cmd * chara[j][1], 0, chara[j][2], chara[j][3], 0)
            # print(j, cmd, cmd * sign[j])

        if r >= 1.0:
            break

        time.sleep(CONTROL_PERIOD)


# ======================================================
# Main
# ======================================================
print("------------------------------------")
print(" Step0 モーターの準備")
print("------------------------------------")

motors = dict()
for m, t in MOTOR_LIST.items():
    m_ = motors_py.MotorDriver.create_motor(
        motor_id=t[0],
        interface_type="can",
        interface="can0",
        motor_type="ROB",
        motor_model=0,
        master_id_offset=0,
    )
    motors[m] = m_
    print(m, t[0], t[1], t[2], t[3])
    chara[m] = t
    

for j in motors.keys():
    print(j, "id", motors[j].get_motor_id())
    motors[j].init_motor()

wait_key("Step1へ進む")


print(" Step1 現在角度")
print("------------------------------------")

for j in motors.keys():
    motors[j].motor_mit_cmd(0, 0, 0, 0 ,0)
        
    # 運動状態を読み取る
    q, dq, tau = read_joint(j)
    error_id = motors[j].get_error_id()
    current_pos[j] = q

    print(
        f"{j:12s} "
        f"{q} {math.degrees(q):7.2f} deg "
        f"{dq:7.2f} rad/s "
        f"{tau:7.2f}"
        f"  sign:{chara[j][1]:2.1f}"
        f"  kp:{chara[j][2]:7.2f}"
        f"  kd:{chara[j][3]:7.2f}"
    )

for j in current_pos.keys():
    print(j, current_pos[j])

wait_key("Step2へ進む")

# ======================================================
# Step2
# ======================================================

print("Move to test posture...")

move_slow(TARGET_POSTURE, MOVE_TIME)

wait_key("Step3へ進む")

# ======================================================
# Step3
# ======================================================

print("Start sinusoidal tests")

center, _, _ = read_joint(TEST_JOINT)
print(center)
wait_key("Step3へ進む")

for freq in FREQ_LIST:

    print("--------------------------------")
    print(f"Frequency : {freq:.2f} Hz")
    print("--------------------------------")

    wait_key(f"{freq:.2f}Hz開始")

    # 一度中心へ戻す
    move_slow(
        {
            TEST_JOINT: center
        },
        2.0
    )

    log = []

    t0 = time.time()

    while True:

        t = time.time() - t0

        if t >= TEST_TIME:
            break

        cmd = center + SIN_AMPLITUDE * math.sin(
            2.0 * math.pi * freq * t
        )


        command_position(TEST_JOINT, cmd)

        q, dq, tau = read_joint(TEST_JOINT)

        log.append([
            t,
            cmd,
            q,
            dq,
            tau
        ])

        time.sleep(CONTROL_PERIOD)

    filename = f"sin_{freq:.1f}Hz.csv"

    with open(filename, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "time",
            "command(rad)",
            "position(rad)",
            "velocity(rad/s)",
            "torque"
        ])

        writer.writerows(log)

    print(f"Saved : {filename}")

print("All tests finished")
# ======================================================
# Step4
# ======================================================

print("Return home")

home = {
    "joint1": 0,
    "joint2": 0,
    "joint3": 0,
    "joint4": 0,
}

move_slow(home, MOVE_TIME)

torque_off()

print("Save CSV")

with open("sin_test.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "time",
        "cmd(rad)",
        "pos(rad)",
        "vel(rad/s)",
        "torque"
    ])

    writer.writerows(log)

print("Done.")