#!/usr/bin/env python3
import motors_py
import time
from calc_ankle import calc_ankle_angle
import numpy as np
import argparse


def example_can_motor():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pitch', default= 0.0)
    parser.add_argument('--roll', default= 0.0)
    args = parser.parse_args()
    print(args.pitch, args.roll)

    print("=== 膝制御のテスト ===")
    motors = []
    try:
        for i in range(0x01, 0x05):
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
        kp_k = 50.0
        kd_k = 2.5
        kp_h = 30.0
        kd_h = 1.0
        torque = 0.0

        da = 0.01
        angle = 0.0
        while True:
            motors[0].motor_mit_cmd(-angle, target_vel, kp_h, kd_h, torque)
            motors[1].motor_mit_cmd(0.0, target_vel, kp_h, kd_h, torque)
            motors[2].motor_mit_cmd(0.0, target_vel, kp_h, kd_h, torque)
            motors[3].motor_mit_cmd(angle, target_vel, kp_k, kd_k, torque)
            angle += da
            if angle < -1.5 or angle > 0.1 :
                da *= -1.0
            time.sleep(0.003)
    except Exception as e:
        print(f"モーター制御中にエラーが発生しました: {e}")
    finally:
        for motor in motors:
            print("モーターを無効にする...")
            motor.deinit_motor()


if __name__ == "__main__":
    example_can_motor()
