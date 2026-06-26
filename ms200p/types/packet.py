from dataclasses import dataclass


@dataclass
class ScanPoint:
    distance: float
    intensity: float

@dataclass
class MS200PPacket:
    speed: float
    start_angle: float
    end_angle: float
    points: list[ScanPoint]