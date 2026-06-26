import math
from sensor_msgs.msg import LaserScan
from ..types.packet import MS200PPacket


class ScanBuilder:
    def __init__(self, frame_id: str, angle_resolution_deg: float, range_min: float, range_max: float, inverted: bool = False):
        self.frame_id = frame_id
        self.range_min = range_min
        self.range_max = range_max
        self.inverted = inverted
        self.angle_res = math.radians(angle_resolution_deg)
        self.num_bins = int(round(2 * math.pi / self.angle_res))
        self.reset()

    def reset(self):
        self.ranges = [math.inf] * self.num_bins
        self.intensities = [0.0] * self.num_bins
        self.last_angle = None
        self.scan_start_time = None

    def build_scan(self, end_time) -> LaserScan:
        msg = LaserScan()
        msg.header.stamp = self.scan_start_time.to_msg()
        msg.header.frame_id = self.frame_id
        msg.angle_min = 0.0
        msg.angle_max = 2 * math.pi - self.angle_res
        msg.angle_increment = self.angle_res
        msg.range_min = self.range_min
        msg.range_max = self.range_max

        scan_time = (end_time - self.scan_start_time).nanoseconds * 1e-9
        if scan_time <= 0:
            scan_time = 0.1
        msg.scan_time = float(scan_time)
        msg.time_increment = float(scan_time / self.num_bins)

        msg.ranges = [float(r) for r in self.ranges]
        msg.intensities = [float(i) for i in self.intensities]

        return msg

    def add_packet(self, packet: MS200PPacket, now) -> LaserScan | None:
        if self.scan_start_time is None:
            self.scan_start_time = now

        diff = packet.end_angle - packet.start_angle
        if diff < 0:
            diff += 360.0

        step = diff / (len(packet.points) - 1)

        scan_to_publish = None

        for i, point in enumerate(packet.points):
            ang_deg = (packet.start_angle + step * i) % 360.0
            ang_rad = math.radians(ang_deg)

            if self.inverted:
                ang_rad = (2 * math.pi - ang_rad) % (2 * math.pi)

            if self.last_angle is not None and ang_rad < self.last_angle - math.pi:
                scan_to_publish = self.build_scan(now)
                self.reset()
                self.scan_start_time = now

            self.last_angle = ang_rad

            bin_idx = int(ang_rad / self.angle_res) % self.num_bins
            if self.range_min <= point.distance <= self.range_max:
                if math.isinf(self.ranges[bin_idx]) or point.distance < self.ranges[bin_idx]:
                    self.ranges[bin_idx] = point.distance
                    self.intensities[bin_idx] = point.intensity

        return scan_to_publish
