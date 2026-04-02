from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split a CSV file into deterministic replay batches."
    )
    parser.add_argument("--input-file", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--batches", type=int, default=4)
    return parser.parse_args()


def split_csv(input_file: Path, output_dir: Path, batches: int) -> dict[str, int]:
    if batches <= 0:
        raise ValueError("batches must be greater than zero")

    output_dir.mkdir(parents=True, exist_ok=True)

    with input_file.open("r", newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError(f"{input_file.name} is missing a header row")

        batch_paths = [
            output_dir / f"replay_batch_{index + 1:02d}.csv" for index in range(batches)
        ]
        batch_files = [path.open("w", newline="", encoding="utf-8") for path in batch_paths]

        try:
            writers = [
                csv.DictWriter(handle, fieldnames=reader.fieldnames)
                for handle in batch_files
            ]
            for writer in writers:
                writer.writeheader()

            counts = {path.name: 0 for path in batch_paths}
            for row_index, row in enumerate(reader):
                batch_index = row_index % batches
                writers[batch_index].writerow(row)
                counts[batch_paths[batch_index].name] += 1
        finally:
            for handle in batch_files:
                handle.close()

    return counts


def main() -> None:
    args = parse_args()
    input_file = args.input_file.resolve()
    output_dir = args.output_dir.resolve()
    counts = split_csv(input_file, output_dir, args.batches)
    manifest_path = output_dir / "replay_manifest.json"
    manifest_path.write_text(json.dumps(counts, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
