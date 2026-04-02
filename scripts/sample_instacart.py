from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path


REQUIRED_FILES = (
    "orders.csv",
    "order_products__prior.csv",
    "order_products__train.csv",
    "products.csv",
    "aisles.csv",
    "departments.csv",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deterministic Instacart sample for RetailPulse."
    )
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--sample-modulus", type=int, default=10)
    parser.add_argument("--sample-remainder", type=int, default=0)
    return parser.parse_args()


def validate_inputs(input_dir: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (input_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required input files: {', '.join(missing)}")


def ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def sample_orders(
    input_path: Path, output_path: Path, modulus: int, remainder: int
) -> tuple[set[int], int]:
    if modulus <= 0:
        raise ValueError("sample-modulus must be greater than zero")
    if not 0 <= remainder < modulus:
        raise ValueError("sample-remainder must be between 0 and sample-modulus - 1")

    order_ids: set[int] = set()
    sampled_rows = 0

    with input_path.open("r", newline="", encoding="utf-8") as source, output_path.open(
        "w", newline="", encoding="utf-8"
    ) as target:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError("orders.csv is missing a header row")
        writer = csv.DictWriter(target, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            user_id = int(row["user_id"])
            if user_id % modulus != remainder:
                continue
            writer.writerow(row)
            order_ids.add(int(row["order_id"]))
            sampled_rows += 1

    return order_ids, sampled_rows


def filter_order_products(input_path: Path, output_path: Path, order_ids: set[int]) -> int:
    kept_rows = 0

    with input_path.open("r", newline="", encoding="utf-8") as source, output_path.open(
        "w", newline="", encoding="utf-8"
    ) as target:
        reader = csv.DictReader(source)
        if reader.fieldnames is None:
            raise ValueError(f"{input_path.name} is missing a header row")
        writer = csv.DictWriter(target, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            order_id = int(row["order_id"])
            if order_id not in order_ids:
                continue
            writer.writerow(row)
            kept_rows += 1

    return kept_rows


def copy_lookup_files(input_dir: Path, output_dir: Path) -> None:
    for name in ("products.csv", "aisles.csv", "departments.csv"):
        shutil.copy2(input_dir / name, output_dir / name)


def write_manifest(output_dir: Path, manifest: dict[str, object]) -> None:
    manifest_path = output_dir / "sample_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()

    validate_inputs(input_dir)
    ensure_output_dir(output_dir)

    sampled_order_ids, sampled_order_count = sample_orders(
        input_dir / "orders.csv",
        output_dir / "orders.csv",
        args.sample_modulus,
        args.sample_remainder,
    )
    prior_count = filter_order_products(
        input_dir / "order_products__prior.csv",
        output_dir / "order_products__prior.csv",
        sampled_order_ids,
    )
    train_count = filter_order_products(
        input_dir / "order_products__train.csv",
        output_dir / "order_products__train.csv",
        sampled_order_ids,
    )
    copy_lookup_files(input_dir, output_dir)

    manifest = {
        "sample_modulus": args.sample_modulus,
        "sample_remainder": args.sample_remainder,
        "sampled_orders": sampled_order_count,
        "sampled_order_ids": len(sampled_order_ids),
        "sampled_prior_rows": prior_count,
        "sampled_train_rows": train_count,
        "lookup_files": ["products.csv", "aisles.csv", "departments.csv"],
    }
    write_manifest(output_dir, manifest)


if __name__ == "__main__":
    main()
