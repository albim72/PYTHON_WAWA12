# generate_events.py
import numpy as np
import pandas as pd

def generate_events(n_rows: int = 5_000_000) -> pd.DataFrame:
    rng = np.random.default_rng(seed=42)

    user_ids = rng.integers(0, 100_000, size=n_rows, dtype=np.int32)

    event_types = np.array(["view", "click", "purchase", "logout"])
    event_type_ids = rng.integers(0, len(event_types), size=n_rows)
    event_type_col = event_types[event_type_ids]

    devices = np.array(["android", "ios", "web"])
    device_ids = rng.integers(0, len(devices), size=n_rows)
    device_col = devices[device_ids]

    # timestamps w ciągu jednego dnia (sekundy 0–86400)
    base = np.datetime64("2025-01-01")
    seconds = rng.integers(0, 86_400, size=n_rows)
    timestamps = base + seconds.astype("timedelta64[s]")

    # amount > 0 tylko dla purchase
    amount = rng.normal(loc=100.0, scale=20.0, size=n_rows)
    amount = np.maximum(amount, 1.0)
    amount[event_type_col != "purchase"] = 0.0

    df = pd.DataFrame({
        "event_id": np.arange(n_rows, dtype=np.int64),
        "user_id": user_ids,
        "event_type": event_type_col,
        "timestamp": timestamps,
        "amount": amount,
        "device": device_col,
    })

    return df

if __name__ == "__main__":
    df = generate_events()
    print(df.head())
    print("Rows:", len(df))

    df.to_parquet("events_5m.parquet", index=False)
    # ewentualnie:
    # df.to_csv("events_5m.csv", index=False)
