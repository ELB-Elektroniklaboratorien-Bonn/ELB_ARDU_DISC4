import serial
import time
from typing import List
import re

import logging

logging.basicConfig(level=logging.INFO)


MINIMUM_FW_VERSION = "0.0.1"


class SpiIO:
    def __init__(self):
        pass

    def do_io_8(self, data_out: int, cs_index: int) -> int:
        pass

    def do_io_24(self, data_out: List[int], cs_index: int) -> List[int]:
        pass


class TestpulserScpi:
    def __init__(self, serial_connection: serial):
        self.ser = serial_connection

    def switch_testpulser(self, on: bool):
        if on:
            scpi_command = "SYST:PUL:ENA\n"
        else:
            scpi_command = "SYST:PUL:DIS\n"

        to_send = scpi_command.encode("ascii")
        self.ser.write(to_send)

        return wait_for_reply(self.ser, "Pulser")


def wait_for_reply(
    serial_connection: serial, line_start: str, timeout: float = 4.0
) -> str:
    start_time = time.time()
    buffer = bytearray()

    while True:
        bytes_waiting = serial_connection.in_waiting
        if bytes_waiting:
            read_size = min(bytes_waiting, 512)
            data = serial_connection.read(read_size)

            if data:
                buffer.extend(data)
                while b"\n" in buffer:
                    line, _, buffer = buffer.partition(b"\n")
                    line = line.decode("ascii", errors="ignore").strip()
                    if line.startswith(line_start):
                        logging.info(f"Answer {line}, took {time.time() - start_time}")
                        return line

        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout waiting for {line_start} response")

        # Small sleep to reduce CPU use but longer than 10us
        time.sleep(0.001)


class SpiIoAScpi(SpiIO):
    """
    SCPI Communication - SPI Module
    """

    def __init__(self, serial_connection: serial):
        self.ser = serial_connection

    def do_io_24(self, data_out: List[int], cs_index: int):
        if len(data_out) != 3:
            raise RuntimeError(
                f"Invalid SPI Data. Expecting list of 3 ints. Provided {data_out}"
            )

        command: int = data_out[0]
        payload: int = data_out[2] + (data_out[1] << 8)

        scpi_string = f"SYST:SPI:SEN {cs_index}, {command}, {payload}\n"
        to_send = scpi_string.encode("ascii")
        self.ser.write(to_send)

        return wait_for_reply(self.ser, "SPIRESP")


class ArduinoScpi:
    """
    Generic SCPI Communication Class
    """

    def __init__(self, port, baudrate=115200, timeout=2, reset=False):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout
        if not reset:
            self.ser.dtr = False
            self.ser.rts = False
        self.ser.open()
        print("Opening...")

    def send_command(self, command):
        if not command.endswith("\n"):
            command += "\n"
        to_send = command.encode("ascii")
        self.ser.write(to_send)

    def read_response(self):
        return self.ser.readline().decode("ascii").strip()

    def query(self, command):
        self.send_command(command)
        return self.read_response()


class ELBArduDiscSCPI(ArduinoScpi):
    """
    SCPI Communication Class specifically for ELB_ARDU_DISC
    """

    def __init__(self, port, baudrate=115200, timeout=2, reset=False):
        super().__init__(port, baudrate, timeout, reset)
        welcome_message = self.ser.read_until(b"\n").decode("utf-8").strip()
        if ELBArduDiscSCPI.check_message_compatibility(welcome_message):
            print("ELB_ARDU_DISC found:")
            print(welcome_message)
        else:
            raise RuntimeError(
                f"Incompatible Hardware. Welcome Message was: {welcome_message}"
            )
        self.spi = SpiIoAScpi(self.ser)
        self.testpulser = TestpulserScpi(self.ser)

    def check_version(version: str, minimum_version: str):
        v_nums = [int(x) for x in version.split(".")]
        min_nums = [int(x) for x in minimum_version.split(".")]
        return v_nums >= min_nums

    def is_version_format(s):
        pattern = r"^\d+\.\d+\.\d+$"
        return bool(re.match(pattern, s))

    def check_message_compatibility(welcome_message: str):
        msg_list = welcome_message.split(",")
        if msg_list[0] != "ELB":
            return False
        if msg_list[1] != "ARDUDISC":
            return False
        if not ELBArduDiscSCPI.is_version_format(msg_list[3]):
            return False
        if not ELBArduDiscSCPI.check_version(msg_list[3], MINIMUM_FW_VERSION):
            return False
        return True


# Usage example:
if __name__ == "__main__":
    scpi = ELBArduDiscSCPI("COM4", reset=True)
    scpi.spi.do_io_24([1, 2, 3], 1)
