# async_pipeline.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple
import pandas as pd
import numpy as np
import time


def process_chunk_sync(chunk: pd.DataFrame, idx: int) -> Tuple[int, dict]:
    """
    Cięższa, synchroniczna funkcja: np. transformacje numpy + agregacje.
    """
    start = time.perf_counter()

    # przykładowa transformacja numpy: z-score dla amount (tylko purchase)
    data = chunk.copy()
    mask = data["event_type"].values == "purchase"
    amount = data["amount"].values.astype(float)

    if mask.sum() > 0:
        purchase_vals = amount[mask]
        mean = purchase_vals.mean()
        std = purchase_vals.std() or 1.0
        amount[mask] = (purchase_vals - mean) / std
        data["amount_z"] = amount
    else:
        data["amount_z"] = 0.0

    # agregacja: średnia amount_z per event_type
    stats = (
        data.groupby("event_type")["amount_z"]
            .mean()
            .to_dict()
    )

    dur = time.perf_counter() - start
    print(f"[SYNC] chunk {idx} processed in {dur:.2f}s")

    return idx, stats


async def process_chunk_async(
    loop: asyncio.AbstractEventLoop,
    pool: ThreadPoolExecutor,
    chunk: pd.DataFrame,
    idx: int
) -> Tuple[int, dict]:
    """
    Asynchroniczny wrapper: zleca pracę do ThreadPoolExecutor.
    """
    return await loop.run_in_executor(pool, process_chunk_sync, chunk, idx)


async def main():
    file_path = "events_5m.parquet"  # lub csv

    # Możesz też użyć read_csv(chunksize=...), dla parquet -> potrzebny inny podział
    # Tu damy prosty przykład z CSV i chunksize – na szkoleniu możesz pokazać oba warianty.
    chunksize = 200_000

    loop = asyncio.get_running_loop()
    max_workers = 4

    # w realu dopasuj workers do IO/CPU
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        tasks = []
        chunk_idx = 0

        print("[MAIN] Starting async pipeline...")

        # przykład z csv (jeśli masz też wersję CSV)
        for chunk in pd.read_csv("events_5m.csv", chunksize=chunksize):
            task = asyncio.create_task(
                process_chunk_async(loop, pool, chunk, chunk_idx)
            )
            tasks.append(task)
            chunk_idx += 1

            # prosty throttling – max N „żywych” chunków na raz
            while len(tasks) >= max_workers * 2:
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED
                )
                for d in done:
                    idx, stats = d.result()
                    print(f"[MAIN] partial result from chunk {idx}: {stats}")
                    tasks.remove(d)

        # czekamy na resztę
        if tasks:
            done, pending = await asyncio.wait(tasks)
            for d in done:
                idx, stats = d.result()
                print(f"[MAIN] final chunk {idx}: {stats}")

        print("[MAIN] Pipeline finished.")

if __name__ == "__main__":
    asyncio.run(main())
