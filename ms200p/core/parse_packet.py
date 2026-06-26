import struct
from ..types.packet import MS200PPacket, ScanPoint

POINTS_PER_PACKET = 12

def parse_packet(pkt: bytes) -> MS200PPacket:
    speed = struct.unpack('<H', pkt[2:4])[0]
    start_angle = struct.unpack('<H', pkt[4:6])[0] / 100.0
    end_angle = struct.unpack('<H', pkt[-5:-3])[0] / 100.0

    points = []
    for i in range(POINTS_PER_PACKET):
        off = 6 + i * 3
        dist_mm, intensity = struct.unpack('<HB',pkt[off:off + 3])

        points.append(
            ScanPoint(
                distance=dist_mm / 1000.0,
                intensity=float(intensity)
            )
        )

    return MS200PPacket(
        speed=float(speed),
        start_angle=start_angle,
        end_angle=end_angle,
        points=points
    )