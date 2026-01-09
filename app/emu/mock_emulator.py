import argparse
import random
import sys
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--duration", type=int, default=15)
    p.add_argument("--hz", type=int, default=15)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--profile", type=str, default="baseline", choices=["baseline", "cache_stress", "timing_bug"])
    args = p.parse_args()

    random.seed(args.seed)
    interval = 1.0 / max(args.hz, 1)
    start = time.time()

    # profile knobs
    latency_bias = 0.0
    cache_bias = 0.0
    error_bias = 0.0

    if args.profile == "cache_stress":
        cache_bias = 0.08
        latency_bias = 8.0
    elif args.profile == "timing_bug":
        latency_bias = 12.0
        error_bias = 0.02

    while time.time() - start < args.duration:
        ts_ms = int((time.time() - start) * 1000)

        ipc = max(0.2, random.gauss(1.2, 0.15))
        cache_miss = min(0.35, max(0.01, random.gauss(0.07 + cache_bias, 0.02)))
        latency_ms = max(5.0, random.gauss(22.0 + latency_bias, 4.5))
        power_w = max(0.5, random.gauss(8.0 + 10.0 * cache_miss, 0.8))

        warnings = 1 if random.random() < (0.03 + cache_bias * 0.2) else 0
        errors = 1 if random.random() < (0.005 + error_bias) else 0

        line = (
            f"ts={ts_ms}ms latency={latency_ms:.2f}ms ipc={ipc:.3f} "
            f"cache_miss={cache_miss:.3f} power={power_w:.2f}W "
            f"warnings={warnings} errors={errors}"
        )
        print(line)
        sys.stdout.flush()
        time.sleep(interval)


if __name__ == "__main__":
    main()
