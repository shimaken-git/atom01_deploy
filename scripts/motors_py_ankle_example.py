#!/usr/bin/env python3
import motors_py
import time
from calc_ankle import calc_ankle_angle
import numpy as np
import argparse


def example_can_motor():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pitch', default= None)
    parser.add_argument('--roll', default= None)
    parser.add_argument('--time', default= 5.0)
    args = parser.parse_args()
    print(args.pitch, args.roll)

    print("=== 足首制御のテスト ===")
    motors = []
    try:
        for i in range(0x05, 0x07):
            motors.append(motors_py.MotorDriver.create_motor(
            motor_id=i,
            interface_type="can",
            interface="can0",
            motor_type="ROB",
            motor_model=0,
            master_id_offset=0,
        ))
        print("モーターが正常に作成されました！")
    except Exception as e:
        print(f"モーターの作成に失敗しました: {e}")
        return
    
    try:
        print("モーターを有効にする...")
        for motor in motors:
            motor.init_motor()
        
        print("\n=== MITモード制御の例 ===")
        motors[0].set_motor_control_mode(motors_py.MotorControlMode.MIT)
        
        target_vel = 0.0
        kp = 20.0
        kd = 3.0
        torque = 0.0

        if args.pitch is not None and args.roll is not None:
            pitch = float(args.pitch)
            roll = float(args.roll)
            in_a, out_a = calc_ankle_angle(roll, pitch)
            print(f"pitch: {pitch}, roll: {roll}, in_a: {in_a}, out_a: {out_a}")
            motors[0].motor_mit_cmd(-out_a, target_vel, kp, kd, torque) #ID5モーターは符号が逆なのでマイナス
            motors[1].motor_mit_cmd(-in_a, target_vel, kp, kd, torque) #ID6モーターは符号が逆なのでマイナス
            time.sleep(float(args.time))
        else:
            da = 0.2
            angle = 0.0
            amp = 0.4
            while True:
                ax = amp * np.sin(angle)
                ay = amp * np.cos(angle)
                in_a, out_a = calc_ankle_angle(ax, ay)
                print(angle, ax, ay, in_a, out_a)
                motors[0].motor_mit_cmd(out_a, target_vel, kp, kd, torque)
                motors[1].motor_mit_cmd(in_a, target_vel, kp, kd, torque)
                angle += da
                if angle > 2 * np.pi:
                    angle = 0.0
                time.sleep(0.05)
    except Exception as e:
        print(f"モーター制御中にエラーが発生しました: {e}")
    finally:
        for motor in motors:
            print("モーターを無効にする...")
            motor.deinit_motor()


if __name__ == "__main__":
    example_can_motor()
