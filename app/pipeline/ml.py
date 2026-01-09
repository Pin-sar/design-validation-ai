from dataclasses import dataclass
from typing import Dict

import numpy as np
from sklearn.ensemble import IsolationForest

from app.core.config import settings


@dataclass
class MLResult:
    anomaly_score: float
    is_anomalous: bool


def detect_anomaly(run_kpis: Dict[str, float]) -> MLResult:
    """
    In real silicon flows, you'd train on historical "golden" runs.
    For a portfolio-safe demo, we train on synthetic neighborhood samples.
    """
    x = np.array([[run_kpis["latency_p95_ms"], run_kpis["cache_miss_mean"], run_kpis["error_rate"]]])

    baseline = np.vstack(
        [
            x + np.random.normal([0.0, 0.0, 0.0], [2.0, 0.01, 0.002], size=(250, 3)),
            x + np.random.normal([6.0, 0.03, 0.006], [3.0, 0.015, 0.004], size=(80, 3)),
        ]
    )

    model = IsolationForest(
        n_estimators=250,
        contamination=settings.ANOMALY_CONTAMINATION,
        random_state=123,
    )
    model.fit(baseline)

    score = float(model.decision_function(x)[0])  # lower => more anomalous
    pred = int(model.predict(x)[0])               # -1 anomalous, 1 normal

    return MLResult(anomaly_score=score, is_anomalous=(pred == -1))
