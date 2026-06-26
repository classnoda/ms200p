# ms200p

ROS 2 driver for the Oradar MS200P 2D LiDAR. Reads data over a serial port, parses it, and publishes standard `sensor_msgs/LaserScan` messages to the `/scan` topic.

### RViz2 Visualization Example
![Scan visualization in RViz](docs/img.png)

## Requirements

- ROS 2 (tested on Jazzy)
- `pyserial` (`python3-serial`)
- `sensor_msgs`, `geometry_msgs`, `tf2_ros`

## Installation

Clone the repository into your ROS 2 workspace and build the package:

```bash
cd ~/ros2_ws/src
git clone <repo_url> ms200p
cd ..
colcon build --packages-select ms200p
source install/setup.bash
```

## Usage

### Via launch file

```bash
ros2 launch ms200p ms200p.launch.py
```

### Directly

```bash
ros2 run ms200p ms200p_node --ros-args -p port:=/dev/ttyACM0
```

### RViz2

```bash
rviz2 -d ~/ros2_ws/src/ms200p/rviz/ms200p.rviz
```

## Parameters

| Parameter              | Type    | Default        | Description                                              |
|------------------------|---------|----------------|----------------------------------------------------------|
| `port`                 | string  | `/dev/ttyACM0` | Serial port device path                                  |
| `baudrate`             | int     | `230400`       | Serial baud rate                                         |
| `frame_id`             | string  | `laser`        | TF frame ID attached to published scans                  |
| `topic`                | string  | `scan`         | Topic name for `LaserScan` messages                      |
| `range_min`            | float   | `0.05`         | Minimum valid range (metres)                             |
| `range_max`            | float   | `12.0`         | Maximum valid range (metres)                             |
| `angle_resolution_deg` | float   | `1.0`          | Angular resolution used when accumulating a full scan    |
| `inverted`             | bool    | `false`        | Flip scan direction (mirror around 0°)                   |
| `publish_tf`           | bool    | `false`        | Publish a static TF transform from `parent_frame`        |
| `parent_frame`         | string  | `base_link`    | Parent frame for the optional static TF transform        |

## Protocol

Each packet from the sensor is 47 bytes long. The packet header is `0x54 0x2C`. Each packet contains 12 scan points, where every point is encoded as two bytes of distance (millimetres, little-endian) and one byte of intensity. The packet also carries a start angle, an end angle, the rotation speed, and a CRC-8 checksum. The driver verifies the checksum before processing a packet and silently discards corrupted frames.

## Project Structure

```
ms200p/
├── docs/
│   ├── img.png                      # RViz2 visualization screenshot
│   └── README.md                    # Original Russian documentation
├── launch/
│   └── ms200p.launch.py             # ROS 2 launch file
├── ms200p/
│   ├── __init__.py
│   ├── node.py                      # Main ROS 2 node (MS200PNode)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── crc.py                   # CRC-8 checksum implementation
│   │   └── parse_packet.py          # Raw bytes → packet struct parser
│   ├── sub_system/
│   │   ├── __init__.py
│   │   ├── scan_builder.py          # Accumulates packets into LaserScan
│   │   └── serial_reader.py         # Serial port reader / framer
│   └── types/
│       ├── __init__.py
│       └── packet.py                # Packet dataclass definition
├── resource/
│   └── ms200p                       # ament resource index marker
├── rviz/
│   └── ms200p.rviz                  # RViz2 configuration
├── test/
│   ├── test_copyright.py
│   ├── test_flake8.py
│   └── test_pep257.py
├── .gitignore
├── LICENSE                          # MIT License
├── package.xml                      # ROS 2 package manifest
├── setup.cfg                        # Python package configuration
└── setup.py                         # ament_python build script
```
## License

MIT