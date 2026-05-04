#!/usr/bin/env python3
import imu_py
import time

def example_serial_imu():
    print("=== serial IMU example ===")
    try:
        imu = imu_py.IMUDriver.create_imu(
            imu_id=8,
            interface_type="serial",
            interface="/dev/ttyUSB0",
            imu_type="WITMOTION",
            baudrate=921600
        )
    except Exception as e:
        print(f"Failed build IMU: {e}")
        return
    
    print(f"IMU ID: {imu.get_imu_id()}")
    
    for i in range(1000):
        quat = imu.get_quat()
        print(f"quaternion: w={quat[0]:.4f}, x={quat[1]:.4f}, y={quat[2]:.4f}, z={quat[3]:.4f}")
        
        ang_vel = imu.get_ang_vel()
        print(f"angle velocity: x={ang_vel[0]:.4f}, y={ang_vel[1]:.4f}, z={ang_vel[2]:.4f} rad/s")
        
        lin_acc = imu.get_lin_acc()
        print(f"linear accelaration: x={lin_acc[0]:.4f}, y={lin_acc[1]:.4f}, z={lin_acc[2]:.4f} m/s^2")
        
        temp = imu.get_temperature()
        print(f"temperature: {temp:.2f}°C")
        
        print("-" * 50)
        time.sleep(0.01)

if __name__ == "__main__":
    example_serial_imu()