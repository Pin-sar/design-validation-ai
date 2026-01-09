import re
from dataclasses import dataclass
from typing import Optional

LINE_RE = re.compile(
    r"ts=(\d+)ms\s+latency=([\d.]+)ms\s+ipc=([\d.]+)\s+cache_miss=([\d.]+)\s+power=([\d.]+)W\s+warnings=(\d+)\s+errors=(\d+)"
)


@dataclass
class ParsedSample:
    ts_ms: int
    latency_ms: float
    ipc: float
    cache_miss: float
    power_w: float
    warnings: int
    errors: int
    raw_line: str


def parse_line(line: str) -> Optional[ParsedSample]:
    line = (line or "").strip()
    m = LINE_RE.match(line)
    if not m:
        return None

    return ParsedSample(
        ts_ms=int(m.group(1)),
        latency_ms=float(m.group(2)),
        ipc=float(m.group(3)),
        cache_miss=float(m.group(4)),
        power_w=float(m.group(5)),
        warnings=int(m.group(6)),
        errors=int(m.group(7)),
        raw_line=line,
    )
