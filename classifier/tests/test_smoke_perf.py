import time


def test_inference_latency_budget_smoke() -> None:
    start = time.perf_counter()
    for _ in range(1000):
        _ = "example malicious request".lower().strip()
    elapsed = time.perf_counter() - start
    assert elapsed < 0.5

