import csv
from pathlib import Path
from typing import Callable

import pandas as pd
from tqdm.auto import tqdm


def run_resumable_batch(
    cities: pd.DataFrame,
    checkpoint_path: str | Path,
    process_row: Callable[[pd.Series], dict],
    stat_keys: list[str],
    key_col: str = "kod",
    desc: str = "Stahování",
) -> pd.DataFrame:
    """
    Iteruje přes řádky `cities`, pro každý zavolá `process_row` a výsledek
    okamžitě připíše do `checkpoint_path` (CSV). Při opětovném spuštění
    přeskočí řádky, jejichž `key_col` už je v checkpointu – lze tedy
    bezpečně přerušit (Ctrl+C, pád kernelu) a navázat odtud, kde to skončilo.

    process_row(row) musí vrátit dict s klíči == stat_keys (hodnoty None při chybě)
    plus klíč "error" (None při úspěchu, jinak text výjimky).
    """
    checkpoint_path = Path(checkpoint_path)

    done_keys: set[str] = set()
    if checkpoint_path.exists():
        existing = pd.read_csv(checkpoint_path, dtype={key_col: str})
        done_keys = set(existing[key_col].astype(str))

    to_process = cities[~cities[key_col].astype(str).isin(done_keys)]
    fieldnames = list(cities.columns) + stat_keys + ["error"]

    write_header = not checkpoint_path.exists()
    with open(checkpoint_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        for _, row in tqdm(to_process.iterrows(), total=len(to_process), desc=desc):
            entry = row.to_dict()
            result = process_row(row)
            entry.update(result)
            writer.writerow(entry)
            f.flush()

    return pd.read_csv(checkpoint_path, dtype={key_col: str})
