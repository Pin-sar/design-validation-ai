import subprocess
from dataclasses import dataclass
from typing import List, Tuple

from app.core.logging import logger
from app.pipeline.parser import parse_line


@dataclass
class CollectResult:
    parsed_rows: List[Tuple]  # (ts_ms, latency_ms, ipc, cache_miss, power_w, warnings, errors, raw_line)
    parse_failures: int
    exit_code: int


def run_emulator_and_collect(cmd: List[str]) -> CollectResult:
    logger.info(f"Launching emulator: {' '.join(cmd)}")

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    parsed_rows: List[Tuple] = []
    failures = 0

    assert p.stdout is not None
    for line in p.stdout:
        s = parse_line(line)
        if not s:
            failures += 1
            continue
        parsed_rows.append((s.ts_ms, s.latency_ms, s.ipc, s.cache_miss, s.power_w, s.warnings, s.errors, s.raw_line))

    rc = p.wait()
    logger.info(f"Emulator exited | code={rc} parsed={len(parsed_rows)} failures={failures}")

    return CollectResult(parsed_rows=parsed_rows, parse_failures=failures, exit_code=rc)
