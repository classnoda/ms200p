import rclpy
import serial
from rclpy.impl.rcutils_logger import RcutilsLogger
from ..core.crc import calc_crc8
from ..core.parse_packet import parse_packet
from ..types.packet import MS200PPacket

PACKET_HEADER = 0x54
PACKET_VERLEN = 0x2C
PACKET_SIZE = 47


class SerialReader:
    def __init__(self, port, baudrate, logger: RcutilsLogger):
        self.logger = logger

        try:
            self.ser = serial.Serial(port, baudrate, timeout=1.0)
            self.buf = bytearray()
        except serial.SerialException as e:
            self.logger.fatal(f'Failed to open port: {e}')
            raise

    def read_packet(self) -> MS200PPacket:
        while rclpy.ok():
            data = self.ser.read(128)
            if data:
                self.buf.extend(data)

            while len(self.buf) >= PACKET_SIZE:
                if self.buf[0] != PACKET_HEADER or self.buf[1] != PACKET_VERLEN:
                    self.buf.pop(0)
                    continue

                pkt = bytes(self.buf[:PACKET_SIZE])
                if calc_crc8(pkt[:-1]) != pkt[-1]:
                    self.buf.pop(0)
                    continue

                del self.buf[:PACKET_SIZE]
                return parse_packet(pkt)

        raise RuntimeError("ROS shutdown")

    def close(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()
