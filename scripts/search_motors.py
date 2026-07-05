#!/usr/bin/env python3
import os
import sys
import yaml
import motors_py
import time
import termios
import tty


def read_key_nonblocking(timeout=0.05):
    import select
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        if select.select([sys.stdin], [], [], timeout)[0]:
            ch = sys.stdin.read(1)
            return ch
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def create_motors(config: dict) -> list:
    motors = []
    motor_ids = config['motor_id']
    motor_interface_type = config['motor_interface_type']
    motor_interfaces = config['motor_interface']
    motor_num = config['motor_num']
    motor_types = config['motor_type']
    motor_models = config['motor_model']
    master_id_offset = config['master_id_offset']
    motor_zero_offsets = config['motor_zero_offset']
    
    motor_idx = 0
    for interface_idx, num in enumerate(motor_num):
        interface = motor_interfaces[interface_idx]
        for _ in range(num):
            if motor_idx >= len(motor_ids):
                break
            motor_id = motor_ids[motor_idx]
            motor_model = motor_models[motor_idx] if motor_idx < len(motor_models) else 0
            motor_type = motor_types[motor_idx]
            motor_zero_offset = motor_zero_offsets[motor_idx] if motor_idx < len(motor_zero_offsets) else 0.0
            
            motor = motors_py.MotorDriver.create_motor(
                motor_id=motor_id,
                interface_type=motor_interface_type,
                interface=interface,
                motor_type=motor_type,
                motor_model=motor_model,
                master_id_offset=master_id_offset,
                motor_zero_offset=motor_zero_offset,
            )
            motors.append({
                'motor': motor,
                'motor_id': motor_id,
                'interface': interface,
                'index': motor_idx
            })
            motor_idx += 1
    
    return motors


def calibrate_motor(motor_info: dict) -> bool:
    motor = motor_info['motor']
    motor_id = motor_info['motor_id']
    interface = motor_info['interface']
    
    print(f"motor ID: {motor_id} port: {interface}")

    motor.init_motor()
    time.sleep(0.3)
    
    motor.set_motor_control_mode(motors_py.MotorControlMode.MIT)
    time.sleep(0.1)
    
    
    zeroed = False
    try:
        motor.motor_mit_cmd(0.0, 0.0, 0.0, 0.0, 0.0)
        time.sleep(0.2)
        pos = motor.get_motor_pos()
        err = motor.get_error_id()
        print(f"\rpos: {pos:+.6f} rad | err: {err}")
        if pos != 0.0:
            zeroed = True
        time.sleep(0.02)
    except KeyboardInterrupt:
        print("\n\nユーザーによる中断")
        motor.deinit_motor()
        raise
    
    motor.deinit_motor()
    time.sleep(0.2)
    
    return zeroed


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config', 'set_zero.yaml')
    
    print(f"\nconfig file: {config_path}\n")
    
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗しました。: {e}")
        return 1
    
    print("設定情報:")
    print(f"  - モーターID列表: {config['motor_id']}")
    print(f"  - モータータイプ: {config['motor_type']}")
    print(f"  - インターフェイスタイプ: {config['motor_interface_type']}")
    print(f"  - インターフェイス: {config['motor_interface']}")
    print(f"  - モーターモデル: {config['motor_model']}")
    print("\n" + "-"*60)
    input("プロセスを開始するには Enterキーを押してください..")
    print("-"*60)
    
    try:
        motors = create_motors(config)
        print(f"\n {len(motors)}個のモーターの作成に成功しました")
    except Exception as e:
        print(f"モーターの作成に失敗しました: {e}")
        return 1
    
    try:
        for motor_info in motors:
            result = calibrate_motor(motor_info)
            if result:
                print(f"motor id {motor_info['motor_id']} found!")
            else:
                print(f"motor id {motor_info['motor_id']} not found!")
    except KeyboardInterrupt:
        print("\n\nユーザーによって中断")
        return 1
    except Exception as e:
        print(f"\nキャリブレーション処理エラー: {e}")
        return 1
    
    print("\n処理終了")
    return 0


if __name__ == '__main__':
    sys.exit(main())
