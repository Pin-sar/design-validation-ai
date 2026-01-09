from app.pipeline.parser import parse_line


def test_parse_line():
    line = "ts=10ms latency=21.20ms ipc=1.234 cache_miss=0.080 power=9.10W warnings=0 errors=1"
    s = parse_line(line)
    assert s is not None
    assert s.ts_ms == 10
    assert abs(s.latency_ms - 21.2) < 1e-6
    assert s.errors == 1
