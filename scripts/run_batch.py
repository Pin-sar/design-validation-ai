import requests

BASE = "http://127.0.0.1:8000/v1"

for profile in ["baseline", "cache_stress", "timing_bug"]:
    r = requests.post(f"{BASE}/runs", json={"profile": profile, "duration_sec": 10, "hz": 20})
    r.raise_for_status()
    run_id = r.json()["run_id"]

    rep = requests.get(f"{BASE}/runs/{run_id}/report").json()

    print("\n==============================")
    print("PROFILE:", profile)
    print("RUN:", run_id)
    print("KPIs:", rep["kpis"])
    print("BOTTLENECKS:", rep["bottlenecks"])
    print("ML:", rep["ml"])
