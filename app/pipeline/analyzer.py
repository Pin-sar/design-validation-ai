from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd

from app.core.config import settings
from app.pipeline.ml import detect_anomaly


@dataclass
class AnalysisReport:
    kpis: Dict[str, float]
    bottlenecks: List[str]
    ml: Dict[str, float]


def analyze_samples(samples: List[dict]) -> AnalysisReport:
    df = pd.DataFrame(samples)
    if df.empty:
        return AnalysisReport(kpis={}, bottlenecks=["No samples collected"], ml={})

    latency_mean = float(df["latency_ms"].mean())
    latency_p95 = float(np.percentile(df["latency_ms"], 95))
    ipc_mean = float(df["ipc"].mean())
    cache_miss_mean = float(df["cache_miss"].mean())

    error_rate = float(df["errors"].sum() / max(len(df), 1))
    warning_rate = float(df["warnings"].sum() / max(len(df), 1))

    kpis = {
        "samples": float(len(df)),
        "latency_mean_ms": latency_mean,
        "latency_p95_ms": latency_p95,
        "ipc_mean": ipc_mean,
        "cache_miss_mean": cache_miss_mean,
        "error_rate": error_rate,
        "warning_rate": warning_rate,
    }

    bottlenecks: List[str] = []

    if latency_p95 > settings.LATENCY_P95_MS_WARN:
        bottlenecks.append(
            f"High tail latency (p95={latency_p95:.2f}ms) → potential timing / critical-path bottleneck."
        )
    if cache_miss_mean > settings.CACHE_MISS_WARN:
        bottlenecks.append(
            f"Elevated cache miss rate (mean={cache_miss_mean:.3f}) → potential memory locality / cache config bottleneck."
        )
    if error_rate > settings.ERROR_RATE_WARN:
        bottlenecks.append(
            f"Error rate high (rate={error_rate:.3f}) → potential functional/timing violations in validation."
        )
    if not bottlenecks:
        bottlenecks.append("No major bottlenecks detected under current thresholds.")

    mlr = detect_anomaly(
        {
            "latency_p95_ms": latency_p95,
            "cache_miss_mean": cache_miss_mean,
            "error_rate": error_rate,
        }
    )

    ml = {"anomaly_score": mlr.anomaly_score, "is_anomalous": float(1 if mlr.is_anomalous else 0)}
    return AnalysisReport(kpis=kpis, bottlenecks=bottlenecks, ml=ml)
