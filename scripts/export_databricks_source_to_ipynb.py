from __future__ import annotations

import argparse
import json
from pathlib import Path


HEADER = "# Databricks notebook source"
CELL_SEPARATOR = "# COMMAND ----------"
MAGIC_PREFIX = "# MAGIC"
MARKDOWN_PREFIX = "# MAGIC %md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic .ipynb files from Databricks source notebooks."
    )
    parser.add_argument("--source-dir", type=Path, default=Path("notebooks"))
    parser.add_argument("--output-dir", type=Path, default=Path("notebooks_ipynb"))
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def iter_notebook_paths(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.glob("*.py") if path.is_file())


def split_databricks_cells(text: str) -> list[list[str]]:
    raw_lines = text.splitlines()
    if raw_lines and raw_lines[0].strip() == HEADER:
        raw_lines = raw_lines[1:]

    cells: list[list[str]] = []
    current: list[str] = []
    for line in raw_lines:
        if line.strip() == CELL_SEPARATOR:
            cells.append(current)
            current = []
            continue
        current.append(line)
    cells.append(current)
    return cells


def first_non_empty_line(lines: list[str]) -> str:
    for line in lines:
        if line.strip():
            return line
    return ""


def markdown_source(lines: list[str]) -> list[str]:
    rendered: list[str] = []
    for line in lines:
        stripped = line.rstrip("\n")
        if stripped.startswith(MARKDOWN_PREFIX):
            remainder = stripped[len(MARKDOWN_PREFIX) :].lstrip()
            if remainder:
                rendered.append(remainder + "\n")
            continue
        if stripped.startswith(f"{MAGIC_PREFIX} "):
            rendered.append(stripped[len(MAGIC_PREFIX) + 1 :] + "\n")
            continue
        if stripped == MAGIC_PREFIX:
            rendered.append("\n")
            continue
        rendered.append(stripped + "\n")
    return rendered


def code_source(lines: list[str]) -> list[str]:
    return [line + "\n" for line in lines]


def build_cell(lines: list[str]) -> dict[str, object]:
    if first_non_empty_line(lines).startswith(MARKDOWN_PREFIX):
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": markdown_source(lines),
        }
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": code_source(lines),
    }


def notebook_payload(source_text: str) -> dict[str, object]:
    cells = [build_cell(lines) for lines in split_databricks_cells(source_text)]
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def rendered_ipynb_text(source_path: Path) -> str:
    payload = notebook_payload(source_path.read_text(encoding="utf-8"))
    return json.dumps(payload, indent=1, ensure_ascii=False) + "\n"


def export_notebooks(source_dir: Path, output_dir: Path, check: bool) -> int:
    source_paths = iter_notebook_paths(source_dir)
    if not source_paths:
        raise FileNotFoundError(f"No Databricks source notebooks found in {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    drift: list[str] = []

    for source_path in source_paths:
        output_path = output_dir / f"{source_path.stem}.ipynb"
        rendered = rendered_ipynb_text(source_path)
        if check:
            if not output_path.exists():
                drift.append(f"missing: {output_path}")
                continue
            existing = output_path.read_text(encoding="utf-8")
            if existing != rendered:
                drift.append(f"out_of_date: {output_path}")
            continue
        with output_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(rendered)

    if drift:
        print("\n".join(drift))
        return 1
    return 0


def main() -> None:
    args = parse_args()
    exit_code = export_notebooks(args.source_dir.resolve(), args.output_dir.resolve(), args.check)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
