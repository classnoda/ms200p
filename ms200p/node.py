#!/usr/bin/env python3
import threading
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from .sub_system.serial_reader import SerialReader
from .sub_system.scan_builder import ScanBuilder


class MS200PNode(Node):
    def __init__(self):
        super().__init__("ms200p_node")

        self.declare_parameter("port", "/dev/ttyACM0")
        self.declare_parameter("baudrate", 230400)
        self.declare_parameter("frame_id", "laser")
        self.declare_parameter("topic", "scan")
        self.declare_parameter("range_min", 0.05)
        self.declare_parameter("range_max", 12.0)
        self.declare_parameter("angle_resolution_deg", 1.0)
        self.declare_parameter("inverted", False)
        self.declare_parameter("publish_tf", False)
        self.declare_parameter("parent_frame", "base_link")

        port = self.get_parameter("port").value
        baudrate = self.get_parameter("baudrate").value
        frame_id = self.get_parameter("frame_id").value
        topic = self.get_parameter("topic").value
        range_min = float(self.get_parameter("range_min").value)
        range_max = float(self.get_parameter("range_max").value)
        angle_resolution_deg = float(self.get_parameter("angle_resolution_deg").value)
        inverted = bool(self.get_parameter("inverted").value)
        publish_tf = bool(self.get_parameter("publish_tf").value)
        parent_frame = self.get_parameter("parent_frame").value

        self.pub = self.create_publisher(LaserScan, topic, qos_profile_sensor_data)

        if publish_tf:
            from tf2_ros import StaticTransformBroadcaster
            from geometry_msgs.msg import TransformStamped

            self.tf_broadcaster = StaticTransformBroadcaster(self)
            tf_msg = TransformStamped()

            tf_msg.header.stamp = self.get_clock().now().to_msg()
            tf_msg.header.frame_id = parent_frame
            tf_msg.child_frame_id = frame_id
            tf_msg.transform.rotation.w = 1.0

            self.tf_broadcaster.sendTransform(tf_msg)

        self.reader = SerialReader(port=port, baudrate=baudrate, logger=self.get_logger())
        self.builder = ScanBuilder(
            frame_id=frame_id,
            angle_resolution_deg=angle_resolution_deg,
            range_min=range_min,
            range_max=range_max,
            inverted=inverted
        )
        self.get_logger().info(f"Opened {port} @ {baudrate}")

        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        while self._running and rclpy.ok():
            try:
                packet = self.reader.read_packet()
                scan = self.builder.add_packet(packet, self.get_clock().now())

                if scan is not None:
                    self.pub.publish(scan)
            except Exception as e:
                self.get_logger().warn(f"Read error: {e}")

    def destroy_node(self):
        self._running = False

        if hasattr(self, "_thread"):
            self._thread.join(timeout=1.0)
        if hasattr(self, "reader"):
            self.reader.close()

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MS200PNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
