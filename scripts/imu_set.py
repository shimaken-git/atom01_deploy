import serial
import time
import argparse


# =========================
# 設定
# =========================

PORT = "/dev/ttyUSB0"
BAUDRATE = 921600

# HWT906 registers
REG_BANDWIDTH = 0x1F
REG_ACCFILT = 0x2A
REG_READADDR = 0x27

# BANDWIDTH
BANDWIDTH_VALUES = {
    256: 0x00,
    188: 0x01,
    98: 0x02,
    42: 0x03,
    20: 0x04,
}


# =========================
# HWT906通信
# =========================

class HWT906:

    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.2
        )

    def close(self):
        self.ser.close()

    def send(self, data):
        data = bytes(data)

        print("TX:", data.hex(" ").upper())

        self.ser.write(data)
        self.ser.flush()

    # -------------------------
    # UNLOCK
    # -------------------------

    def unlock(self):
        # FF AA 69 88 B5
        self.send([
            0xFF,
            0xAA,
            0x69,
            0x88,
            0xB5
        ])

        time.sleep(0.05)

    # -------------------------
    # SAVE
    # -------------------------

    def save(self):
        # FF AA 00 00 00
        self.send([
            0xFF,
            0xAA,
            0x00,
            0x00,
            0x00
        ])

        time.sleep(0.2)

    # -------------------------
    # レジスタ書き込み
    # -------------------------

    def write_register(self, address, value):
        """
        HWT906 register write

        FF AA ADDR LOW HIGH
        """

        low = value & 0xFF
        high = (value >> 8) & 0xFF

        self.send([
            0xFF,
            0xAA,
            address,
            low,
            high
        ])

        time.sleep(0.05)

    # -------------------------
    # レジスタ読み出し
    # -------------------------

    def read_register(self, address):
        """
        READADDR(0x27) に読みたいレジスタを指定。

        HWT906は指定レジスタから4レジスタ分を返す。

        Response:

            55 5F
            REG1_L REG1_H
            REG2_L REG2_H
            REG3_L REG3_H
            REG4_L REG4_H
            SUM
        """

        # 受信バッファをクリア
        self.ser.reset_input_buffer()

        # FF AA 27 ADDR 00
        self.send([
            0xFF,
            0xAA,
            REG_READADDR,
            address,
            0x00
        ])

        time.sleep(0.1)

        # 十分な量を読む
        data = self.ser.read(128)

        if data:
            print("RX:", data.hex(" ").upper())
        else:
            print("RX: timeout")
            return None

        # 55 5F を探す
        for i in range(len(data) - 10):

            if data[i] != 0x55 or data[i + 1] != 0x5F:
                continue

            frame = data[i:i + 11]

            if len(frame) != 11:
                continue

            # checksum
            checksum = sum(frame[0:10]) & 0xFF

            if checksum != frame[10]:
                print(
                    f"Invalid checksum: "
                    f"calculated=0x{checksum:02X}, "
                    f"received=0x{frame[10]:02X}"
                )
                continue

            # 4つのレジスタ
            values = []

            for j in range(4):
                low = frame[2 + j * 2]
                high = frame[3 + j * 2]

                value = low | (high << 8)
                values.append(value)

            print(
                f"Read 0x{address:02X}: "
                + " ".join(
                    f"0x{v:04X}" for v in values
                )
            )

            # 目的のレジスタはREG1
            return values[0]

        print("55 5F response not found")

        return None


# =========================
# 現在の設定を表示
# =========================

def print_current_settings(imu):

    print("\n=== Current register values ===")

    bandwidth = imu.read_register(REG_BANDWIDTH)
    accfilt = imu.read_register(REG_ACCFILT)

    print()

    # BANDWIDTH
    if bandwidth is not None:

        bandwidth_name = None

        for hz, reg_value in BANDWIDTH_VALUES.items():
            if reg_value == bandwidth:
                bandwidth_name = hz
                break

        if bandwidth_name is not None:
            print(
                f"BANDWIDTH : {bandwidth_name} Hz "
                f"(register = 0x{bandwidth:04X})"
            )
        else:
            print(
                f"BANDWIDTH : unknown "
                f"(register = 0x{bandwidth:04X})"
            )

    else:
        print("BANDWIDTH : read error")

    # ACCFILT
    if accfilt is not None:
        print(
            f"ACCFILT   : {accfilt}"
        )
    else:
        print("ACCFILT   : read error")


# =========================
# 引数
# =========================

def parse_args():

    parser = argparse.ArgumentParser(
        description="HWT906 register configuration tool"
    )

    # 読み出しモード
    parser.add_argument(
        "--read",
        action="store_true",
        help="現在の設定を読み出して表示するだけ"
    )

    # BANDWIDTH
    parser.add_argument(
        "--bandwidth",
        type=int,
        choices=BANDWIDTH_VALUES.keys(),
        help="BANDWIDTH [Hz]: 20, 42, 98, 188, 256"
    )

    # ACCFILT
    parser.add_argument(
        "--accfilt",
        type=int,
        help="ACCFILT value"
    )

    args = parser.parse_args()

    # --read と設定変更を同時指定しない
    if args.read and (
        args.bandwidth is not None
        or args.accfilt is not None
    ):
        parser.error(
            "--read と --bandwidth / --accfilt は同時に指定できません"
        )

    # --read でない場合は両方必須
    if not args.read:

        if args.bandwidth is None:
            parser.error(
                "--bandwidth を指定してください"
            )

        if args.accfilt is None:
            parser.error(
                "--accfilt を指定してください"
            )

    return args


# =========================
# メイン
# =========================

def main():

    args = parse_args()

    imu = HWT906(
        PORT,
        BAUDRATE
    )

    try:

        # =====================
        # READ ONLY
        # =====================

        if args.read:

            print_current_settings(imu)

            return

        # =====================
        # SETTING
        # =====================

        bandwidth_reg = BANDWIDTH_VALUES[
            args.bandwidth
        ]

        print("\n=== Configuration ===")

        print(
            f"BANDWIDTH : "
            f"{args.bandwidth} Hz "
            f"(0x{bandwidth_reg:04X})"
        )

        print(
            f"ACCFILT   : "
            f"{args.accfilt}"
        )

        # ---------------------
        # 現在値
        # ---------------------

        print_current_settings(imu)

        # ---------------------
        # UNLOCK
        # ---------------------

        print("\n=== UNLOCK ===")

        imu.unlock()

        # ---------------------
        # WRITE
        # ---------------------

        print("\n=== WRITE ===")

        # BANDWIDTH
        imu.write_register(
            REG_BANDWIDTH,
            bandwidth_reg
        )

        # ACCFILT
        imu.write_register(
            REG_ACCFILT,
            args.accfilt
        )

        # ---------------------
        # WRITE後確認
        # ---------------------

        print("\n=== Read after WRITE ===")

        print_current_settings(imu)

        # ---------------------
        # SAVE
        # ---------------------

        print("\n=== SAVE ===")

        imu.save()

        # ---------------------
        # SAVE後確認
        # ---------------------

        print("\n=== Read after SAVE ===")

        print_current_settings(imu)

    finally:

        imu.close()


if __name__ == "__main__":
    main()
