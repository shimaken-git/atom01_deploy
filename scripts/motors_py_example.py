#!/usr/bin/env python3
import motors_py
import time

def example_can_motor():
    """CANバス経由で接続されたモーターの例"""
    print("=== CANモーターの例 ===")
    motors = []
    try:
        for i in range(1, 2):
            motors.append(motors_py.MotorDriver.create_motor(
            motor_id=i,
            interface_type="can",
            interface="can0",
            motor_type="DM",
            motor_model=0,
            master_id_offset=16,
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
        
        target_pos = -0.5
        target_vel = 0.0
        kp = 5.0
        kd = 1.0
        torque = 0.0
        
        motors[0].motor_mit_cmd(target_pos, target_vel, kp, kd, torque)
            
        # 運動状態を読み取る
        pos = motors[0].get_motor_pos()
        vel = motors[0].get_motor_spd()
        current = motors[0].get_motor_current()
        temp = motors[0].get_motor_temperature()
        error_id = motors[0].get_error_id()
        
        print(f"位置: {pos:.4f} rad, 速度: {vel:.4f} rad/s, "
              f"電流: {current:.4f} A, 温度: {temp:.2f}°C, エラーコード: {error_id}")
        time.sleep(1)
    except Exception as e:
        print(f"モーター制御中にエラーが発生しました: {e}")
    finally:
        for motor in motors:
            print("モーターを無効にする...")
            motor.deinit_motor()


if __name__ == "__main__":
    example_can_motor()
